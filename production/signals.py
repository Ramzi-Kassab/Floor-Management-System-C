"""
Production Department Signals
==============================
Automatic actions triggered by model events
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

from . import models
from .routing_logic import auto_generate_route_steps, RouteGenerator

logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.JobCard)
def auto_generate_routes_on_jobcard_creation(sender, instance, created, **kwargs):
    """
    Automatically generate route steps when a new job card is created

    This signal handler is triggered after a JobCard is saved.
    For new job cards, it automatically generates route steps based on:
    - Bit design features
    - Order type (new build vs repair)
    - Bit condition (for repairs)
    """
    if created:
        # Only generate routes for new job cards
        logger.info(
            f"New job card created: {instance.jobcard_code}. "
            f"Generating route steps..."
        )

        try:
            steps = auto_generate_route_steps(instance)
            logger.info(
                f"Successfully generated {len(steps)} route steps "
                f"for job card {instance.jobcard_code}"
            )
        except Exception as e:
            logger.error(
                f"Failed to generate route steps for job card {instance.jobcard_code}: {e}",
                exc_info=True
            )


@receiver(post_save, sender=models.EvaluationSummary)
def adjust_route_after_evaluation(sender, instance, created, **kwargs):
    """
    Adjust route steps after evaluation is completed

    When an evaluation is saved, this handler:
    - Adjusts existing route steps based on condition
    - Removes unnecessary steps for minor damage
    - Marks steps as skipped for scrap items
    """
    if created:
        logger.info(
            f"Evaluation created for job card {instance.job_card.jobcard_code}. "
            f"Condition: {instance.overall_condition}. "
            f"Adjusting route..."
        )

        try:
            generator = RouteGenerator(instance.job_card)
            generator.adjust_route_after_evaluation(instance)
            logger.info(
                f"Successfully adjusted route for job card {instance.job_card.jobcard_code} "
                f"based on evaluation"
            )
        except Exception as e:
            logger.error(
                f"Failed to adjust route for job card {instance.job_card.jobcard_code}: {e}",
                exc_info=True
            )


@receiver(post_save, sender=models.WorkOrder)
def update_jobcard_status_on_workorder_completion(sender, instance, **kwargs):
    """
    Update related job cards when work order status changes
    """
    if instance.status == models.WorkOrderStatus.COMPLETED:
        # Mark all job cards as completed
        incomplete_jobcards = instance.job_cards.exclude(
            status=models.JobCardStatus.COMPLETED
        )

        if incomplete_jobcards.exists():
            logger.warning(
                f"Work order {instance.wo_number} marked as COMPLETED "
                f"but has {incomplete_jobcards.count()} incomplete job cards"
            )

    elif instance.status == models.WorkOrderStatus.CANCELLED:
        # Mark all job cards that are not started as cancelled
        logger.info(
            f"Work order {instance.wo_number} cancelled. "
            f"Updating related job cards..."
        )
        # Note: We don't have CANCELLED status for JobCard yet
        # This is a placeholder for future enhancement


@receiver(post_save, sender=models.BitReceive)
def track_bit_location_on_receive(sender, instance, created, **kwargs):
    """
    Automatically create location history entry when bit is received
    """
    if created and instance.bit_instance:
        logger.info(
            f"Bit received: {instance.bit_instance.serial_number}. "
            f"Creating location history entry."
        )

        try:
            models.BitLocationHistory.objects.create(
                bit_instance=instance.bit_instance,
                location_status=models.BitLocationStatus.RECEIVING_INSPECTION,
                changed_by=instance.received_by,
                work_order=instance.work_order,
                receive_transaction=instance,
                physical_location="Receiving Department",
                notes=f"Received via {instance.receive_number}"
            )

            # Update bit instance status
            instance.bit_instance.status = models.BitInstanceStatus.IN_REPAIR
            instance.bit_instance.save()

            logger.info(
                f"Location history created for bit {instance.bit_instance.serial_number}"
            )
        except Exception as e:
            logger.error(
                f"Failed to create location history for receive {instance.receive_number}: {e}",
                exc_info=True
            )


@receiver(post_save, sender=models.BitRelease)
def track_bit_location_on_release(sender, instance, created, **kwargs):
    """
    Automatically create location history entry when bit is released
    """
    if instance.bit_instance:
        # Track status changes
        if instance.status == models.ReleaseStatus.READY:
            location_status = models.BitLocationStatus.READY_FOR_RELEASE
            notes = f"Ready for dispatch via {instance.release_number}"
        elif instance.status == models.ReleaseStatus.DISPATCHED:
            location_status = models.BitLocationStatus.IN_TRANSIT_SHIPPING
            notes = f"Dispatched to {instance.customer_name} via {instance.transport_company}"
        elif instance.status == models.ReleaseStatus.DELIVERED:
            location_status = models.BitLocationStatus.WITH_CUSTOMER
            notes = f"Delivered to {instance.customer_name}"

            # Update bit instance status
            instance.bit_instance.status = models.BitInstanceStatus.WITH_CUSTOMER
            instance.bit_instance.save()
        else:
            return  # Don't track DRAFT or CANCELLED

        logger.info(
            f"Bit release status changed to {instance.status}: "
            f"{instance.bit_instance.serial_number}"
        )

        try:
            # Check if this exact status change already exists (avoid duplicates)
            recent_entry = models.BitLocationHistory.objects.filter(
                bit_instance=instance.bit_instance,
                location_status=location_status,
                release_transaction=instance
            ).first()

            if not recent_entry:
                models.BitLocationHistory.objects.create(
                    bit_instance=instance.bit_instance,
                    location_status=location_status,
                    changed_by=instance.prepared_by,
                    work_order=instance.work_order,
                    release_transaction=instance,
                    physical_location=instance.delivery_address if location_status == models.BitLocationStatus.WITH_CUSTOMER else "Shipping Department",
                    notes=notes
                )

                logger.info(
                    f"Location history created for bit {instance.bit_instance.serial_number}: "
                    f"{location_status}"
                )
        except Exception as e:
            logger.error(
                f"Failed to create location history for release {instance.release_number}: {e}",
                exc_info=True
            )


@receiver(post_save, sender=models.JobCard)
def track_bit_location_on_jobcard_status(sender, instance, **kwargs):
    """
    Track bit location when job card status changes
    """
    if instance.work_order.bit_instance and instance.status == models.JobCardStatus.IN_PROGRESS:
        try:
            # Check if already tracked for this job card
            recent_entry = models.BitLocationHistory.objects.filter(
                bit_instance=instance.work_order.bit_instance,
                job_card=instance,
                location_status=models.BitLocationStatus.IN_PRODUCTION
            ).first()

            if not recent_entry:
                models.BitLocationHistory.objects.create(
                    bit_instance=instance.work_order.bit_instance,
                    location_status=models.BitLocationStatus.IN_PRODUCTION,
                    work_order=instance.work_order,
                    job_card=instance,
                    physical_location=f"{instance.get_department_display()} - {instance.current_workstation or 'N/A'}",
                    notes=f"Job card {instance.jobcard_code} started"
                )

                logger.info(
                    f"Location tracked: Bit {instance.work_order.bit_instance.serial_number} "
                    f"in production at {instance.get_department_display()}"
                )
        except Exception as e:
            logger.error(
                f"Failed to track location for job card {instance.jobcard_code}: {e}",
                exc_info=True
            )

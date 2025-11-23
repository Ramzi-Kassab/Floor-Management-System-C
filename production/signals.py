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

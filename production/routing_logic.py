"""
Production Routing Logic
========================
Intelligent route generation based on bit design features, order type, and condition.

This module handles:
- Automatic route template selection
- Dynamic route step generation
- Conditional routing for repairs
- Process filtering based on bit features
"""

from django.db import transaction
from typing import Optional, List
import logging

from . import models

logger = logging.getLogger(__name__)


class RouteGenerator:
    """
    Intelligent route generation based on bit features and order context
    """

    def __init__(self, job_card: models.JobCard):
        self.job_card = job_card
        self.work_order = job_card.work_order
        self.design = self.work_order.design_revision.design
        self.order_type = self.work_order.order_type

    def generate_route_steps(self) -> List[models.JobRouteStep]:
        """
        Main entry point: Generate all route steps for this job card

        Returns:
            List of created JobRouteStep instances
        """
        # Select appropriate route template
        route_template = self._select_route_template()

        if not route_template:
            logger.warning(
                f"No route template found for job card {self.job_card.jobcard_code}. "
                f"Bit type: {self.design.bit_type}, "
                f"Body material: {self.design.body_material}, "
                f"Order type: {self.order_type}"
            )
            return []

        logger.info(
            f"Selected route template '{route_template.name}' "
            f"for job card {self.job_card.jobcard_code}"
        )

        # Get template steps
        template_steps = route_template.steps.all().order_by('sequence')

        # Filter steps based on conditions
        filtered_steps = self._filter_steps_by_conditions(template_steps)

        # Create actual route steps
        created_steps = []
        with transaction.atomic():
            for step_template in filtered_steps:
                route_step = self._create_route_step(step_template)
                created_steps.append(route_step)

        logger.info(
            f"Generated {len(created_steps)} route steps "
            f"for job card {self.job_card.jobcard_code}"
        )

        return created_steps

    def _select_route_template(self) -> Optional[models.RouteTemplate]:
        """
        Select the most appropriate route template based on:
        - Bit type (PDC vs Roller Cone)
        - Body material (Matrix vs Steel) - for PDC bits
        - Order type (New Build vs Repair)
        - Bit size (future: could have size-specific routes)
        """
        # Start with base filters
        queryset = models.RouteTemplate.objects.filter(
            active=True,
            bit_type=self.design.bit_type,
            for_order_type=self.order_type
        )

        # For PDC bits, filter by body material
        if self.design.bit_type == models.BitType.PDC and self.design.body_material:
            # First try exact match with body material
            exact_match = queryset.filter(
                body_material=self.design.body_material
            ).first()

            if exact_match:
                return exact_match

            # Fallback to any route for this bit type
            fallback = queryset.filter(
                body_material__in=['', self.design.body_material]
            ).first()

            if fallback:
                return fallback

        # For Roller Cone or if no PDC match found
        return queryset.first()

    def _filter_steps_by_conditions(
        self,
        template_steps
    ) -> List[models.RouteStepTemplate]:
        """
        Filter route steps based on bit features and repair conditions

        Examples:
        - Steel-body PDC: Skip infiltration steps
        - Minor damage repair: Skip heavy machining
        - Major damage repair: Include full rebuild steps
        - Evaluation-only: Only include inspection steps
        """
        filtered_steps = []

        for step in template_steps:
            if self._should_include_step(step):
                filtered_steps.append(step)
            else:
                logger.info(
                    f"Skipping step '{step.process_code}' for job card "
                    f"{self.job_card.jobcard_code} based on conditions"
                )

        return filtered_steps

    def _should_include_step(self, step: models.RouteStepTemplate) -> bool:
        """
        Determine if a specific step should be included
        """
        process_code = step.process_code.upper()

        # Rule 1: Steel-body PDC bits skip infiltration-related steps
        if self.design.body_material == models.BodyMaterial.STEEL:
            infiltration_processes = [
                'MOLD_PREP', 'POWDER_LOADING', 'INFILTRATION',
                'COOLING', 'MOLD_REMOVAL'
            ]
            if process_code in infiltration_processes:
                logger.debug(
                    f"Skipping {process_code} for steel-body bit "
                    f"{self.job_card.jobcard_code}"
                )
                return False

        # Rule 2: Evaluation-only orders only include evaluation/inspection steps
        if self.order_type == models.OrderType.EVALUATION_ONLY:
            evaluation_processes = [
                'VISUAL_INSPECTION', 'NDT', 'THREAD_INSPECTION',
                'DIMENSION_CHECK', 'EVALUATION', 'FINAL_QC'
            ]
            if process_code not in evaluation_processes:
                return False

        # Rule 3: Repair-specific logic based on evaluation
        if self.order_type == models.OrderType.REPAIR:
            return self._should_include_repair_step(step)

        # Rule 4: New build - include all applicable steps
        # (already filtered by route template selection)

        # By default, include the step
        return True

    def _should_include_repair_step(self, step: models.RouteStepTemplate) -> bool:
        """
        Conditional logic for repair jobs based on evaluation
        """
        # Try to get the most recent evaluation
        evaluation = self.job_card.evaluations.order_by('-evaluation_date').first()

        if not evaluation:
            # No evaluation yet - include all steps for now
            # This allows evaluation to be performed first
            return True

        process_code = step.process_code.upper()
        condition = evaluation.overall_condition

        # Minor damage: Skip heavy manufacturing processes
        if condition == models.OverallCondition.MINOR_DAMAGE:
            heavy_processes = [
                'INFILTRATION', 'MACHINING', 'MOLD_PREP',
                'POWDER_LOADING', 'MAJOR_WELD'
            ]
            if process_code in heavy_processes:
                logger.info(
                    f"Skipping heavy process {process_code} for minor damage repair "
                    f"{self.job_card.jobcard_code}"
                )
                return False

        # Major damage: Include all rebuild processes
        elif condition == models.OverallCondition.MAJOR_DAMAGE:
            # Include everything - similar to new build
            pass

        # Scrap: Only include evaluation and scrap documentation
        elif condition == models.OverallCondition.SCRAP:
            scrap_processes = ['EVALUATION', 'SCRAP_DOCUMENTATION', 'FINAL_QC']
            if process_code not in scrap_processes:
                return False

        return True

    def _create_route_step(
        self,
        step_template: models.RouteStepTemplate
    ) -> models.JobRouteStep:
        """
        Create a JobRouteStep from a template
        """
        route_step = models.JobRouteStep.objects.create(
            job_card=self.job_card,
            template=step_template,
            sequence=step_template.sequence,
            process_code=step_template.process_code,
            description=step_template.description,
            department=step_template.default_department,
            workstation=step_template.default_workstation,
            status=models.RouteStepStatus.PENDING
        )

        return route_step

    def adjust_route_after_evaluation(self, evaluation: models.EvaluationSummary):
        """
        Adjust existing route steps after evaluation is completed

        This method can be called when evaluation results become available
        to remove unnecessary steps or add required ones.
        """
        if evaluation.overall_condition == models.OverallCondition.SCRAP:
            # Cancel all pending production steps
            self.job_card.route_steps.filter(
                status=models.RouteStepStatus.PENDING
            ).exclude(
                process_code__in=['EVALUATION', 'SCRAP_DOCUMENTATION', 'FINAL_QC']
            ).update(
                status=models.RouteStepStatus.SKIPPED
            )
            logger.info(
                f"Marked steps as SKIPPED for scrapped bit "
                f"{self.job_card.jobcard_code}"
            )

        elif evaluation.overall_condition == models.OverallCondition.MINOR_DAMAGE:
            # Remove heavy manufacturing steps if still pending
            heavy_processes = [
                'INFILTRATION', 'MACHINING', 'MOLD_PREP',
                'POWDER_LOADING', 'MAJOR_WELD'
            ]
            removed_count = self.job_card.route_steps.filter(
                status=models.RouteStepStatus.PENDING,
                process_code__in=heavy_processes
            ).delete()[0]

            if removed_count > 0:
                logger.info(
                    f"Removed {removed_count} heavy process steps for minor damage "
                    f"repair {self.job_card.jobcard_code}"
                )


def auto_generate_route_steps(job_card: models.JobCard) -> List[models.JobRouteStep]:
    """
    Convenience function to auto-generate route steps for a job card

    Args:
        job_card: JobCard instance to generate routes for

    Returns:
        List of created JobRouteStep instances
    """
    generator = RouteGenerator(job_card)
    return generator.generate_route_steps()


def regenerate_route_steps(job_card: models.JobCard) -> List[models.JobRouteStep]:
    """
    Delete existing route steps and regenerate them

    Useful when job card configuration changes or evaluation results arrive

    Args:
        job_card: JobCard instance to regenerate routes for

    Returns:
        List of newly created JobRouteStep instances
    """
    with transaction.atomic():
        # Delete existing pending steps
        deleted_count = job_card.route_steps.filter(
            status=models.RouteStepStatus.PENDING
        ).delete()[0]

        if deleted_count > 0:
            logger.info(
                f"Deleted {deleted_count} existing route steps for "
                f"job card {job_card.jobcard_code}"
            )

        # Generate new steps
        return auto_generate_route_steps(job_card)

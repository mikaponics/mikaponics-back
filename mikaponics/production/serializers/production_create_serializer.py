# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string  # HTML / TXT
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from foundation.models import CropLifeCycleStage, CropDataSheet, CropSubstrate, Device, Production, ProductionCrop


class ProductionCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    description = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    is_commercial = serializers.BooleanField(required=False)
    device_slug = serializers.SlugField(required=True, allow_blank=False, allow_null=False)
    environment = serializers.IntegerField(required=True)
    type_of = serializers.IntegerField(required=True)
    type_of_other = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    grow_system = serializers.IntegerField(required=True)
    grow_system_other = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    has_day_and_night_cycle = serializers.BooleanField(required=False)
    day_starts_at = serializers.TimeField(required=False, allow_null=True,)
    day_finishes_at = serializers.TimeField(required=False, allow_null=True,)
    plants_array = serializers.JSONField(required=True)
    fish_array = serializers.JSONField(required=True)
    inspections_start_at = serializers.DateTimeField(required=True, allow_null=False,)
    inspection_frequency = serializers.IntegerField(required=True, allow_null=False)
    yellow_below_value = serializers.FloatField(required=False, allow_null=True)
    orange_below_value = serializers.FloatField(required=False, allow_null=True)
    red_below_value = serializers.FloatField(required=True, allow_null=False)
    red_alert_delay_in_seconds = serializers.IntegerField(required=True, allow_null=False)
    orange_alert_delay_in_seconds = serializers.IntegerField(required=False, allow_null=False)
    yellow_alert_delay_in_seconds = serializers.IntegerField(required=False, allow_null=False)

    class Meta:
        model = Production
        fields = (
            'name',
            'description',
            'is_commercial',
            'device_slug',
            'environment',
            'type_of',
            'type_of_other',
            'grow_system',
            'grow_system_other',
            'has_day_and_night_cycle',
            'day_starts_at',
            'day_finishes_at',
            'plants_array',
            'fish_array',
            'inspections_start_at',
            'inspection_frequency',
            'yellow_below_value',
            'orange_below_value',
            'red_below_value',
            'red_alert_delay_in_seconds',
            'orange_alert_delay_in_seconds',
            'yellow_alert_delay_in_seconds'
        )

    def validate_device_slug(self, value):
        if not Device.objects.filter(slug=value, user=self.context['authenticated_by']).exists():
            raise exceptions.ValidationError(_('Device does not exist for this device.'))
        return value

    def validate_grow_system_other(self, value):
        if self.context['grow_system'] == Production.GROW_SYSTEM.OTHER_SYSTEM:
            if value == None or value == '':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value

    def validate_type_of_other(self, value):
        if self.context['type_of'] == Production.TYPE_OF.OTHER:
            if value == None or value == '':
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value

    def create(self, validated_data):
        # Get our validated data and context data.
        name = validated_data.get('name', None)
        description = validated_data.get('description', None)
        is_commercial = validated_data.get('is_commercial', False)
        device_slug = validated_data.get('device_slug', None)
        authenticated_by = self.context['authenticated_by']
        authenticated_from = self.context['authenticated_from']
        authenticated_from_is_public = self.context['authenticated_from_is_public']
        environment = validated_data.get('environment', None)
        type_of = validated_data.get('type_of', None)
        type_of_other = validated_data.get('type_of_other', None)
        grow_system = validated_data.get('grow_system', None)
        grow_system_other = validated_data.get('grow_system_other', None)
        has_day_and_night_cycle = validated_data.get('has_day_and_night_cycle', None)
        day_starts_at = validated_data.get('day_starts_at', None)
        day_finishes_at = validated_data.get('day_finishes_at', None)
        plants_array = validated_data.get('plants_array', [])
        fish_array = validated_data.get('fish_array', [])

        device = Device.objects.get(slug=device_slug)

        inspections_start_at = validated_data.get('inspections_start_at', None)
        inspection_frequency = validated_data.get('inspection_frequency', None)
        yellow_below_value = validated_data.get('yellow_below_value', None)
        orange_below_value = validated_data.get('orange_below_value', None)
        red_below_value = validated_data.get('red_below_value', None)
        red_alert_delay_in_seconds = validated_data.get('red_alert_delay_in_seconds', None)
        orange_alert_delay_in_seconds = validated_data.get('orange_alert_delay_in_seconds', None)
        yellow_alert_delay_in_seconds = validated_data.get('yellow_alert_delay_in_seconds', None)

        production = Production.objects.create(
            user=authenticated_by,
            device=device,
            name=name,
            description=description,
            is_commercial=is_commercial,
            environment=environment,
            type_of=type_of,
            type_of_other=type_of_other,
            grow_system=grow_system,
            grow_system_other=grow_system_other,
            started_at=timezone.now(),
            state=Production.PRODUCTION_STATE.OPERATING,
            has_day_and_night_cycle=has_day_and_night_cycle,
            day_starts_at=day_starts_at,
            day_finishes_at=day_finishes_at,
            created_by=authenticated_by,
            created_from=authenticated_from,
            created_from_is_public=authenticated_from_is_public,
            last_modified_by=authenticated_by,
            last_modified_from=authenticated_from,
            last_modified_from_is_public=authenticated_from_is_public,
            inspections_start_at=inspections_start_at,
            inspection_frequency=inspection_frequency,
            yellow_below_value=yellow_below_value,
            orange_below_value=orange_below_value,
            red_below_value=red_below_value,
            red_alert_delay_in_seconds=red_alert_delay_in_seconds,
            orange_alert_delay_in_seconds=orange_alert_delay_in_seconds,
            yellow_alert_delay_in_seconds=yellow_alert_delay_in_seconds,
        )

        # Generate the next inspection date and attach it to the production.
        production.next_inspection_at = production.generate_next_inspection_datetime()
        production.save()

        # Save our plants.
        for plant in plants_array:
            data_sheet = CropDataSheet.objects.filter(slug=plant['plant_slug']).first()
            substrate = CropSubstrate.objects.filter(slug=plant['substrate_slug']).first()
            stage = CropLifeCycleStage.objects.filter(slug=plant['stage_slug']).first()
            production_crop = ProductionCrop.objects.create(
                production=production,
                stage=stage,
                data_sheet=data_sheet,
                data_sheet_other=plant.get('plant_other', None),
                variety=plant.get('variety', None),
                quantity=plant['quantity'],
                substrate=substrate,
                substrate_other=plant.get('substrate_other', None),
                type_of=ProductionCrop.TYPE_OF.PLANT
            )

        # Save our fish.
        for fish in fish_array:
            data_sheet = CropDataSheet.objects.filter(slug=fish['fish_slug']).first()
            substrate = CropSubstrate.objects.filter(slug=fish['substrate_slug']).first()
            stage = CropLifeCycleStage.objects.filter(slug=fish['stage_slug']).first()
            production_crop = ProductionCrop.objects.create(
                production=production,
                stage=stage,
                data_sheet=data_sheet,
                data_sheet_other=fish.get('fish_other', None),
                quantity=fish['quantity'],
                substrate=substrate,
                substrate_other=fish.get('substrate_other', None),
                type_of=ProductionCrop.TYPE_OF.FISHSTOCK
            )

        # DEVELOPERS NOTES:
        # (1) This is  a "Serializer" and not "ModelSerializer" as a result we
        #     will attach the object we created in this serializer.
        # (2) In the output, you can get the object we created.
        validated_data['slug'] = production.slug
        validated_data['production'] = production # ATTACH OBJECT WE CREATED IN THIS SERIALIZER.
        return validated_data

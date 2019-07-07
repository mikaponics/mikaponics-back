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

from foundation.models import ProductionCrop, ProductionInspection, Production
from production.serializers.production_crop_inspection_create_serializer import ProductionCropInspectionCreateSerializer


class ProductionInspectionCreateSerializer(serializers.ModelSerializer):
    production = serializers.SlugRelatedField(
        many=False,
        slug_field='slug',
        queryset=Production.objects.all(),
        allow_null=False,
    )
    slug = serializers.SlugField(read_only=True,)
    state = serializers.IntegerField(read_only=True,)
    did_pass = serializers.BooleanField(required=True,)
    failure_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True,)
    notes = serializers.CharField(required=False, allow_blank=True)
    crop_inspections = serializers.JSONField(required=True, allow_null=False)

    class Meta:
        model = ProductionInspection
        fields = (
            'production',
            'slug',
            'state',
            'did_pass',
            'failure_reason',
            'notes',
            'crop_inspections',
        )

    def validate_failure_reason(self, value):
        """
        Validation enforces that the `failure_reason` field gets filled out
        if the user selected `did_pass=True`.
        """
        if self.context.get("did_pass", None) == False:
            if value == "" or value == None:
                print("ProductionInspectionCreateSerializer - validate_failure_reason - failed")
                raise exceptions.ValidationError(_('Please fill in this field.'))
        return value

    def create(self, validated_data):
        # # Get our validated data and context data.
        user = self.context.get('authenticated_by')
        ip = self.context.get('authenticated_from')
        ip_from_is_public = self.context.get('authenticated_from_is_public')
        production = validated_data.get('production', None)
        did_pass = validated_data.get('did_pass', None)
        failure_reason = validated_data.get('failure_reason', None)
        notes = validated_data.get('notes', None)
        crop_inspections = validated_data.get('crop_inspections', None)

        # Step 1: Create our inspection.
        inspection = ProductionInspection.objects.get_or_create(
            production=production,
            state=ProductionInspection.STATE.SUBMITTED,
            did_pass=did_pass,
            failure_reason=failure_reason,
            notes=notes,
            created_by=user,
            created_from=ip,
            created_from_is_public=ip_from_is_public,
            last_modified_by=user,
            last_modified_from=ip,
            last_modified_from_is_public=ip_from_is_public,
            at_duration=production.get_runtime_duration()
        )

        # Step 2: Create our crop inspections.
        self.process_crop_inspections(inspection, user, ip, ip_from_is_public, crop_inspections)

        # Step 3: Return our created object.
        return inspection

    def process_crop_inspections(self, inspection, user, ip, ip_from_is_public, crop_inspections):
        '''
        Function iterates through all the crop inspections we have and
        serializes them and then saves them to the database.
        '''
        for crop_inspection in crop_inspections:
            crop_inspection['inspection'] = inspection
            serializer = ProductionCropInspectionCreateSerializer(data=crop_inspection, context={
                'authenticated_by': user,
                'authenticated_from': ip,
                'authenticated_from_is_public': ip_from_is_public,
                'review': crop_inspection.get('review', None),
            })
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.save()

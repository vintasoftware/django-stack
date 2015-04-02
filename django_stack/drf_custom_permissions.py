# coding: utf-8

from rest_framework import permissions


class CustomViewPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if hasattr(view, 'custom_permission'):
            return view.custom_permission(request)
        return False

    def has_object_permission(self, request, view, obj):
        if hasattr(view, 'custom_object_permission'):
            return view.custom_object_permission(request, obj)
        return False

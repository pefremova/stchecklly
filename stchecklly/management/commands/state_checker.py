# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from stchecklly.command import add_arguments, _main


class Command(BaseCommand):

    def add_arguments(self, parser):

        add_arguments(parser)

    def handle(self, *args, **kwargs):
        _main(**kwargs)

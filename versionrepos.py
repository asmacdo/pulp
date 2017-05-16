#!/usr/bin/env python3

"""
Usage:
    $ pclean && python -m unittest versionrepos.py
"""

import os
import unittest

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pulp.app.settings')

django.setup()

from pulp.app.models import *


class TestVR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c1 = Content.objects.create()
        cls.c2 = Content.objects.create()

        cls.r1 = Repository.objects.create(name='r1')
        cls.r2 = Repository.objects.create(name='r2')
        cls.r3 = Repository.objects.create(name='r3')
        cls.overlap = Repository.objects.create(name='overlap')


        cls.r1v1 = RepositoryVersion.objects.create(repository=cls.r1, num=1, action='upload')
        cls.r1v2 = RepositoryVersion.objects.create(repository=cls.r1, num=2, action='upload')
        cls.r2v1 = RepositoryVersion.objects.create(repository=cls.r2, num=1, action='upload')
        cls.r3v1 = RepositoryVersion.objects.create(repository=cls.r3, num=1, action='upload')
        cls.r3v2 = RepositoryVersion.objects.create(repository=cls.r3, num=2, action='upload')
        cls.r3v3 = RepositoryVersion.objects.create(repository=cls.r3, num=3, action='upload')
        cls.r3v4 = RepositoryVersion.objects.create(repository=cls.r3, num=4, action='upload')
        cls.overlap_1 = RepositoryVersion.objects.create(repository=cls.overlap, num=1, action='upload')
        cls.overlap_2 = RepositoryVersion.objects.create(repository=cls.overlap, num=2, action='upload')

        cls.rc1 = RepositoryContent.objects.create(repository=cls.r1, content=cls.c1,
                                                   vadded=cls.r1v1, vremoved=cls.r1v2,)
        cls.rc2 = RepositoryContent.objects.create(repository=cls.r1, content=cls.c2,
                                                   vadded=cls.r1v1)
        cls.rc3 = RepositoryContent.objects.create(repository=cls.r2, content=cls.c1,
                                                   vadded=cls.r2v1)
        cls.rc4 = RepositoryContent.objects.create(repository=cls.r2, content=cls.c2,
                                                   vadded=cls.r2v1)
        cls.oc1 = RepositoryContent.objects.create(repository=cls.overlap, content=cls.c1,
                                                   vadded=cls.overlap_1)
        cls.oc2 = RepositoryContent.objects.create(repository=cls.overlap, content=cls.c1,
                                                   vadded=cls.overlap_2)

        # test adding, removing, adding, removing the same content from a repo
        cls.rc5 = RepositoryContent.objects.create(repository=cls.r3, content=cls.c1,
                                                   vadded=cls.r3v1, vremoved=cls.r3v2)
        cls.rc6 = RepositoryContent.objects.create(repository=cls.r3, content=cls.c1,
                                                   vadded=cls.r3v3, vremoved=cls.r3v4)

    def test_r1v1_content(self):
        """
        Just a version with both content items.
        """
        content = self.r1v1.content()
        self.assertTrue(self.c1 in content)
        self.assertTrue(self.c2 in content)

    def test_r1v2_content(self):
        """
        Next version, and one of them has been removed.
        """
        content = self.r1v2.content()
        self.assertTrue(self.c1 not in content)
        self.assertTrue(self.c2 in content)

    def test_r2v1_content(self):
        """
        Different repo with the same content. Make sure they're both associated.
        """
        content = self.r2v1.content()
        self.assertTrue(self.c1 in content)
        self.assertTrue(self.c2 in content)

    def test_r3v1_content(self):
        content = self.r3v1.content()
        self.assertTrue(self.c1 in content)

    def test_r3v2_content(self):
        content = self.r3v2.content()
        self.assertTrue(self.c1 not in content)

    def test_r3v3_content(self):
        content = self.r3v3.content()
        self.assertTrue(self.c1 in content)

    def test_r3v4_content(self):
        content = self.r3v4.content()
        self.assertTrue(self.c1 not in content)

    def test_overlap_1(self):
        content = self.overlap_1.content()
        self.assertTrue(self.c1 in content)
        self.assertEqual(len(content), 1)

    def test_overlap_2(self):
        content = self.overlap_2.content()
        self.assertTrue(self.c1 in content)
        self.assertEqual(len(content), 1)

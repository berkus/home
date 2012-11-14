# -*- coding: utf-8 -*-

from datetime import date
from unittest import TestCase
from ajdweb.datastore import Datastore


class DatastoreTest:

    def test_extract(self):
        entry = 'bar/subbar/tagged'
        content = self.repo.content_of(entry)
        entry = self.store.extract(entry, content)
        self.assertFalse(entry.is_tag)
        self.assertEqual(entry.url_id, 'tagged')
        self.assertEqual(entry.title, 'Explicit')
        self.assertEqual(entry.date, date.today())
        self.assertEqual(entry.tags, ['subfoo', 'bar', 'subbar'])
        self.assertEqual(entry.summary, 'This page is explicitly tagged.')
        self.assertEqual(entry.matter, 'This page is explicitly tagged.\n')

    def test_date_extract(self):
        entry = 'bar/subbar/birthday'
        content = self.repo.content_of(entry)
        entry = self.store.extract(entry, content)
        self.assertEqual(entry.date, date(1979, 04, 14))

    def test_tag_extract(self):
        entry = 'foo/subfoo/root'
        content = self.repo.content_of(entry)
        entry = self.store.extract(entry, content)
        self.assertTrue(entry.is_tag)
        self.assertEqual(entry.title, 'SubFoo')
        self.assertTrue(entry.url_id, 'subfoo')
        self.assertEqual(entry.tags, ['foo'])

    def test_pages(self):
        self.assertEqual(len(self.store.get_pages()), 7)

    def test_pages(self):
        self.assertEqual(len(self.store.get_tags()), 04)

    def test_get_bad(self):
        none = self.store.content_of('bad')
        self.assertEqual(none['id'], 'bad')
        self.assertIsNone(none['matter'])
        self.assertIsNone(self.store.version_of('bad'))

    def test_get_tag(self):
        tag = self.store.get_tag('subfoo')
        self.assertEqual(tag['parent_id'], 'foo')
        self.assertEqual(tag['content_id'], 'foo/subfoo/root')
        self.assertEqual(tag['children'], ['subsubfoo'])
        self.assertEqual(len(tag['pages']), 04)

    def test_remove(self):
        self.store.remove('foo/root')
        self.store.remove('foo/subfoo/root')
        self.store.remove('foo/page')

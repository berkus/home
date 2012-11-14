# -*- coding: utf-8 -*-

from datetime import date, datetime


class Datastore:

    ''' The common base for all datastore implementations. '''

    class Entry:

        ''' A datastore entry.'''

        def __init__(self, entry):
            self.tags = []
            self.title = None
            self.matter = None
            self.is_tag = False
            self.summary = None
            self.date = date.today()
            components = entry.split('/')
            if components[-1] == 'root':
                self.is_tag = True
                self.url_id = (components[-2] if len(components) > 1 else '')
                self.tags = ([components[-3]] if len(components) > 2 else [])
            else:
                self.url_id = components[-1]
                self.tags.extend(components[:-1])

    def extract(self, e, lines):
        ''' Populate the entry from the contents read from the repository. '''

        entry = Datastore.Entry(e)

        meta = {}
        index = 0

        while True:
            line = lines[index]
            index = index + 1
            if len(line) == 0:
                break  # the first empty line ends meta section
            for marker in ['title:', 'date:', 'tags:']:
                if line.lower().startswith(marker):
                    meta[marker[:-1]] = line[len(marker):].strip()

        if 'title' in meta:
            entry.title = meta['title']
        else:
            entry.title = lines[0].strip()  # the first line is the default title

        if 'tags' in meta:
            for t in meta['tags'].split(','):
                entry.tags.append(t.strip())

        entry.tags = list(set(entry.tags))  # get rid of duplicates

        if 'date' in meta:
            for form in ['%b %d, %Y', '%b %d %Y']:
                try:
                    entry.date = datetime.strptime(meta['date'], form).date()
                    break
                except:
                    pass

        entry.matter = '\n'.join(lines[index:])  # everything after meta is the matter

        # everything after the meta block and the first empty line is the summary
        meta['summary'] = []
        while index < len(lines):
            line = lines[index]
            index = index + 1
            if len(line) == 0:
                break
            meta['summary'].append(line)

        entry.summary = '\n'.join(meta['summary'])

        return entry

    def synchronize(self, repository):
        ''' Update the datastore with the changes in the repository '''

        changes = []

        if self.version() != repository.version():

            here = self.ids()
            there = repository.ids()

            for entry in here - there:
                self.remove(entry)
                changes.append(('remove', entry))

            for entry in there - here:
                content = repository.content_of(entry)
                version = repository.version_of(entry)
                self.add(entry, version, content)
                changes.append(('add', entry))

            for entry in here & there:
                if repository.version_of(entry) != self.version_of(entry):
                    content = repository.content_of(entry)
                    version = repository.version_of(entry)
                    self.update(entry, version, content)
                    changes.append(('update', entry))

            self.record_change(repository.version(), changes)

        return changes

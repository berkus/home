# -*- coding: utf-8 -*-


class Database:

    def synchronize(self, repo):
        updates = []
        repo_version = repo.version()
        if self.version() != repo_version:
            here = self.pages()
            there = repo.pages()
            for page in there - here:
                updates.append(self.add(page, repo.content_of(page)))
            for page in here - there:
                updates.append(self.remove(page))
            for page in [o for o in here & there if repo.version_of(o) != self.version_of(o)]:
                updates.append(self.change(page, repo.content_of(page)))

        return (self.record(repo_version, updates) if updates else None)

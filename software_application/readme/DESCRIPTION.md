Manage your internal and third-party software catalog directly in Odoo.

- Register applications with website links, notes, tags, and images.
- Link each application to a product to reuse sales description data.
- Track release history with semantic versions, release dates, notes, and download URLs.
- Group applications by type and attach resource applications when relevant.

## Technical details

**Application catalog**

The module defines the model software.application with application metadata,
product linkage, tags, image storage, and release/resource relations. The
write override resets product and tag links when switching to the other type,
and clears related resources when the new type no longer allows resources.

**Release management**

The module defines software.application.release with SQL uniqueness constraints
on version and URL per application. It uses semver to parse and rebuild version
components (major, minor, patch, prerelease, build), computes metadata fields
from version, and recomputes version when metadata fields change.

**Default release content**

Default values are generated for version, date, release notes, and URL. Release
notes are built from standard sections and item lists, while default versioning
can inspect context-provided release commands and existing release ids to bump
the next major semantic version.

**Tags**

The software.tag model provides translatable labels and color indexing with a
uniqueness SQL constraint on the tag name.

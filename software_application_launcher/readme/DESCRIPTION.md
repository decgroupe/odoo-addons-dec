This module extends the software catalog so you can publish launcher applications and expose a launcher manifest API.

- Adds a new Launcher application type and a dedicated menu to manage launchers.
- Lets you attach linked applications, tooltip images, corner/pictogram images, and launcher flags like Free, Soon, and license-required.
- Provides API endpoints that return launcher manifests with applications/resources, optionally including tooltip images.
- Protects the built-in Tool tag from deletion to keep launcher tagging consistent.

## Technical details

**Software application model extensions**

The module inherits software.application and adds launcher-specific fields: application_ids, image_ids, corner_image, pictogram_image, is_free, is_soon, and need_license. It extends allowed_types_for_resources() to include launcher and overrides write() to clear launcher image data when the type is changed to other.

**Manifest payload builder**

software.application._get_launcher_manifest_entry() centralizes payload generation for API responses. It builds tags, resources, releases, and optional tooltipImages, and marks entries as tools when the record has tag software_application_launcher.tag_tool.

**Launcher APIs (v1 and v2)**

Controller endpoints in controllers/sal_api_v1.py and controllers/sal_api_v2.py expose JSON routes under /api/launcher/v1 and /api/launcher/v2 with api_key authentication. V1 keeps backward-compatible filtering behavior; V2 is launcher-centric and selects a launcher by identifier, then returns linked applications plus their resources, with optional per-asset filtering and image payloads.

**Image helper model and UI**

Model software.application.image stores tooltip images and computes resized_image via tools.image_process(). The form and inherited application views add launcher pages, tooltip image kanban management, and related display options.

**Tag protection**

Model software.tag is introduced with a unique name constraint and an unlink() guard that raises a UserError when trying to remove the protected tool tag.

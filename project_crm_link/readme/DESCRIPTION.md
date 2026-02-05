This module links CRM opportunities and projects so teams can navigate both sides
of the relationship quickly.

- Add an Opportunity Link field on projects to connect a project to an existing
	CRM opportunity.
- Show a Related Projects tab on opportunities to list and manage linked
	projects from the opportunity form.
- Add a Related Projects smart button on opportunities for quick access to the
	linked projects list.
- Extend project search and grouping so users can filter and group projects by
	linked opportunity.

## Technical details

**CRM opportunity integration**

The module extends crm.lead with related_project_ids and
related_project_count. It adds action_view_related_projects to open linked
projects with a domain on linked_lead_id and context defaults (including
bypass_supermanager_check and default_partner_id when relevant).

**Project link model and name/search enrichment**

The module extends project.project with linked_lead_id and opportunity_ids.
It enriches project lookup by extending _get_typefast_domain to include
linked_lead_id.search_name and appends the linked opportunity complete name in
_get_name_identifications.

**View changes**

The module inherits CRM and Project views to expose linked fields in forms and
search views, add a Related Projects page and smart button on opportunities, and
add a dedicated group by filter on linked_lead_id.

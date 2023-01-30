# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""BibTex Schema formaters, helper file for schema.py file."""


class BibTexFormatter:
    """Helper formater class for parsing all the following types.

    publication
    publication_annotationcollection
    publication_book
    publication_section
    publication_conferencepaper
    publication_datamanagementplan
    publication_article
    publication_patent
    publication_preprint
    publication_deliverable
    publication_milestone
    publication_proposal
    publication_report
    publication_softwaredocumentation
    publication_taxonomictreatment
    publication_technicalnote
    publication_thesis
    publication_workingpaper
    publication_other
    poster
    presentation
    dataset
    image
    image_figure
    image_plot
    image_drawing
    image_diagram
    image_photo
    image_other
    video
    software
    lesson
    other.
    """

    def format(name, req_fields, opt_fields):
        """Basic output formater for BibTexFormatter."""
        return {
            "name": name,
            "req_fields": req_fields,
            "opt_fields": opt_fields,
        }

    # def publication():
    #     return BibTexFormatter.other()

    # def publication_annotationcollection():
    #     return BibTexFormatter.other()

    def publication_book():
        """Format book entry type. A book with an explicit publisher."""
        name = "book"
        req_fields = ["author", "title", "publisher", "year"]
        opt_fields = ["volume", "address", "month", "note"]
        return format(name, req_fields, opt_fields)

    # def publication_section():
    #     return BibTexFormatter.other()

    # def publication_conferencepaper():
    #     return BibTexFormatter.other()

    # def publication_datamanagementplan():
    #     return BibTexFormatter.other()

    def publication_article():
        """Format article entry type. An article from a journal or magazine."""
        name = "article"
        req_fields = ["author", "title", "journal", "year"]
        opt_fields = ["volume", "number", "pages", "month", "note"]
        return format(name, req_fields, opt_fields)

    # def publication_patent():
    #     return BibTexFormatter.other()

    # def publication_preprint():
    #     return BibTexFormatter().other()

    # def publication_deliverable():
    #     return BibTexFormatter().other()

    # def publication_milestone():
    #     return BibTexFormatter().other()

    # def publication_proposal():
    #     return BibTexFormatter().other()

    # def publication_report():
    #     return BibTexFormatter().other()

    # def publication_softwaredocumentation():
    #     return BibTexFormatter().other()

    # def publication_taxonomictreatment():
    #     return BibTexFormatter().other()

    # def publication_technicalnote():
    #     return BibTexFormatter().other()

    def publication_thesis():
        """Format article entry type. An article from a journal or magazine."""
        name = "phdthesis"
        req_fields = ["author", "title", "school", "year"]
        opt_fields = ["address", "month", "note"]
        return format(name, req_fields, opt_fields)

    # def publication_other():
    #     return BibTexFormatter().other()

    # def poster():
    #     return BibTexFormatter().other()

    # def presentation():
    #     return BibTexFormatter().other()

    def dataset():
        """Format dataset entry type."""
        name = "dataset"
        req_fields = []
        opt_fields = [
            "author",
            "title",
            "month",
            "year",
            "note",
            "publisher",
            "version",
        ]
        return format(name, req_fields, opt_fields)

    # def image_figure():
    #     return BibTexFormatter().other()

    # def image_plot():
    #     return BibTexFormatter().other()

    # def image_drawing():
    #     return BibTexFormatter().other()

    # def image_diagram():
    #     return BibTexFormatter().other()

    # def image_photo():
    #     return BibTexFormatter().other()

    # def image_other():
    #     return BibTexFormatter().other()

    # def video():
    #     return BibTexFormatter().other()

    def software():
        """Format software entry type."""
        name = "software"
        req_fields = []
        opt_fields = [
            "author",
            "title",
            "month",
            "year",
            "note",
            "publisher",
            "version",
        ]
        return format(name, req_fields, opt_fields)

    # def lesson():
    #     return BibTexFormatter().other()

    def other():
        """Format misc entry type. For use when nothing else fits."""
        name = "misc"
        req_fields = []
        opt_fields = [
            "author",
            "title",
            "month",
            "year",
            "note",
            "publisher",
            "version",
        ]
        return BibTexFormatter.format(name, req_fields, opt_fields)

    ''' Zenodo legacy fields not handled above
    def _format_booklet():
        """Format article entry type. A work that is printed and bound, but without a named publisher or sponsoring institution."""
        name = "booklet"
        req_fields = ["title"]
        opt_fields = ["author", "address", "month", "year", "note"]
        return format(name, req_fields, opt_fields)

    def _format_proceedings():
        """Format article entry type. The proceedings of a conference."""
        name = "proceedings"
        req_fields = ["title", "year"]
        opt_fields = ["publisher", "address", "month", "note"]
        return format(name, req_fields, opt_fields)

    def _format_inproceedings():
        """Format article entry type. An article in the proceedings of a conference."""
        name = "inproceedings"
        req_fields = ["author", "title", "booktitle", "year"]
        opt_fields = ["pages", "publisher", "address", "month", "note", "venue"]
        return format(name, req_fields, opt_fields)

    def _format_unpublished():
        """Format article entry type. A document with an author and title, but not formally published."""
        name = "unpublished"
        req_fields = ["author", "title", "note"]
        opt_fields = ["month", "year"]

        return format(name, req_fields, opt_fields)

    def _format_manual():
        """Format article entry type. Technical documentation."""
        name = "manual"
        req_fields = ["title"]
        opt_fields = ["author", "address", "month", "year", "note"]
        return format(name, req_fields, opt_fields)
'''

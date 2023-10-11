# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging
import operator
from tempfile import TemporaryFile
from os.path import splitext

from odoo import api, fields, models, tools, sql_db, _
from odoo.exceptions import UserError
from odoo.tools.translate import TranslationImporter

_logger = logging.getLogger(__name__)


class BaseLanguageImport(models.TransientModel):
    _name = "base.language.import"
    _description = "Language Import"

    name = fields.Char('Language Name', required=True)
    code = fields.Char('ISO Code', size=6, required=True,
                       help="ISO Language and Country code, e.g. en_US")
    data = fields.Binary('File', required=True, attachment=False)
    filename = fields.Char('File Name', required=True)
    overwrite = fields.Boolean('Overwrite Existing Terms',
                               default=True,
                               help="If you enable this option, existing translations (including custom ones) "
                                    "will be overwritten and replaced by those in this file")

    def import_lang(self):
<<<<<<< HEAD
        Lang = self.env["res.lang"]
        for overwrite, base_lang_imports in tools.groupby(self, operator.itemgetter('overwrite')):
            translation_importer = TranslationImporter(self.env.cr)
            for base_lang_import in base_lang_imports:
                if not Lang._activate_lang(base_lang_import.code):
                    Lang._create_lang(base_lang_import.code, lang_name=base_lang_import.name)
                try:
                    with TemporaryFile('wb+') as buf:
                        buf.write(base64.decodebytes(base_lang_import.data))
                        fileformat = splitext(base_lang_import.filename)[-1][1:].lower()
                        translation_importer.load(buf, fileformat, base_lang_import.code)
                except Exception as e:
                    _logger.warning('Could not import the file due to a format mismatch or it being malformed.')
                    raise UserError(
                        _('File %r not imported due to format mismatch or a malformed file.'
                          ' (Valid formats are .csv, .po, .pot)\n\nTechnical Details:\n%s') % \
                        (base_lang_import.filename, tools.ustr(e))
                    )
            translation_importer.save(overwrite=overwrite)
=======
        this = self[0]
        with TemporaryFile('wb+') as buf:
            try:
                buf.write(base64.decodebytes(this.data))

                # now we determine the file format
                buf.seek(0)
                fileformat = os.path.splitext(this.filename)[-1][1:].lower()

                Lang = self.env["res.lang"]
                lang = Lang._activate_lang(self.code) or Lang._create_lang(
                    self.code, lang_name=self.name
                )

                tools.trans_load_data(
                    this._cr, buf, fileformat, this.code, overwrite=self.overwrite
                )
            except ProgrammingError as e:
                _logger.exception('Could not import the file due to a format mismatch or it being malformed.')

                with closing(sql_db.db_connect(self._cr.dbname).cursor()) as cr:
                    raise UserError(_('File %r not imported due to a malformed file.\n\n'
                                      'This issue can be caused by duplicates entries who are referring to the same field. '
                                      'Please check the content of the file you are trying to import.\n\n'
                                      'Technical Details:\n%s') % (self.filename, tools.ustr(e)))
            except Exception as e:
                _logger.warning('Could not import the file due to a format mismatch or it being malformed.')
                raise UserError(
                    _('File %r not imported due to format mismatch or a malformed file.'
                      ' (Valid formats are .csv, .po, .pot)\n\nTechnical Details:\n%s') % \
                    (this.filename, tools.ustr(e))
                )
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        return True

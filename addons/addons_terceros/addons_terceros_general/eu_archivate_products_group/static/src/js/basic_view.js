odoo.define('eu_archivate_products_group.BasicView', function (require) {
    "use strict";
    
    var session = require('web.session');
    var BasicView = require('web.BasicView');
    BasicView.include({
            init: function(viewInfo, params) {
                var self = this;
                this._super.apply(this, arguments);
                var models_to_deny_archive_partner=['res.partner'];

                var models_to_deny_archive_product=['product.template','product.product'];
                var models_to_deny_duplicate=['sale.order','account.move'];

                var models_to_deny_duplicate_test=models_to_deny_duplicate.includes(self.controllerParams.modelName);
                var model_archivate =  models_to_deny_archive_partner.includes(self.controllerParams.modelName);
                var model_archivate_product =  models_to_deny_archive_product.includes(self.controllerParams.modelName);

                var model_export = self.controllerParams.modelName in ['product.template'] ? 'True' : 'False';

                if(model_archivate) {
                    session.user_has_group('eu_archivate_products_group.archive_contacts').then(function(has_group) {
                        if(!has_group) {
                            self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
                        }
                    });
                    
                };
                if(model_archivate_product) {
                    session.user_has_group('eu_archivate_products_group.archive_products_eu').then(function(has_group) {
                        console.log(has_group);
                        if(!has_group) {
                            self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
                        }
                    });
                    
                };

                

                
                
                    
                
            },
    });
    });
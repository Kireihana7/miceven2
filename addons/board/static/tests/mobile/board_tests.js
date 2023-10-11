<<<<<<< HEAD
/** @odoo-module **/

import { getFixture } from "@web/../tests/helpers/utils";
import { makeView, setupViewRegistries } from "@web/../tests/views/helpers";

let serverData;
let target;

QUnit.module("Board", (hooks) => {
    hooks.beforeEach(async () => {
        target = getFixture();

        serverData = {
            models: {
=======
odoo.define("board.dashboard_tests", function (require) {
    "use strict";

    var BoardView = require("board.BoardView");
    var testUtils = require("web.test_utils");
    var createView = testUtils.createView;

    QUnit.module("Board view", {
        beforeEach: function () {
            this.data = {
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                board: {
                    fields: {},
                    records: [],
                },
                partner: {
                    fields: {
                        foo: {
                            string: "Foo",
                            type: "char",
                            default: "My little Foo Value",
                            searchable: true,
                        },
                    },
                    records: [
                        {
                            id: 1,
                            foo: "yop",
                        },
                    ],
                },
<<<<<<< HEAD
            },
            views: {
                "partner,100000001,form": "<form/>",
                "partner,100000002,search": "<search/>",
            },
        };
        setupViewRegistries();
    });

    QUnit.module("BoardView");

    QUnit.test("can't switch views in the dashboard", async (assert) => {
        serverData.views["partner,4,list"] = '<tree string="Partner"><field name="foo"/></tree>';

        await makeView({
            serverData,
            type: "form",
            resModel: "board",
            arch: `
                <form string="My Dashboard" js_class="board">
                    <board style="2-1">
                        <column>
                            <action context="{&quot;orderedBy&quot;: [{&quot;name&quot;: &quot;foo&quot;, &quot;asc&quot;: True}]}" view_mode="list" string="ABC" name="51" domain="[['foo', '!=', 'False']]"></action>
                        </column>
                    </board>
                </form>`,
            mockRPC(route, args) {
                if (route === "/web/action/load") {
                    return Promise.resolve({
                        res_model: "partner",
                        views: [[4, "list"]],
                    });
                }
            },
        });

        assert.containsNone(target, ".o-dashboard-header", "Couldn't allow user to Change layout");
        assert.containsOnce(target, ".o-dashboard-layout-1", "The display layout is force to 1");
        assert.isNotVisible(
            target.querySelector(".o-dashboard-action .o_control_panel"),
            "views in the dashboard do not have a control panel"
        );
        assert.containsNone(
            target,
            ".o-dashboard-action-header .fa-close",
            "Should not have a close action button"
        );
    });

    QUnit.test("Correctly soft switch to '1' layout on small screen", async function (assert) {
        serverData.views["partner,4,list"] = '<tree string="Partner"><field name="foo"/></tree>';

        await makeView({
            serverData,
            type: "form",
            resModel: "board",
            arch: `
                <form string="My Dashboard" js_class="board">
                    <board style="2-1">
                        <column>
                            <action context="{&quot;orderedBy&quot;: [{&quot;name&quot;: &quot;foo&quot;, &quot;asc&quot;: True}]}" view_mode="list" string="ABC" name="51" domain="[['foo', '!=', 'False']]"></action>
                        </column>
                        <column>
                            <action context="{&quot;orderedBy&quot;: [{&quot;name&quot;: &quot;foo&quot;, &quot;asc&quot;: True}]}" view_mode="list" string="ABC" name="51" domain="[['foo', '!=', 'False']]"></action>
                        </column>
                    </board>
                </form>`,
            mockRPC(route, args) {
                if (route === "/web/action/load") {
                    return Promise.resolve({
                        res_model: "partner",
                        views: [[4, "list"]],
                    });
                }
            },
        });
        assert.containsOnce(target, ".o-dashboard-layout-1", "The display layout is force to 1");
        assert.containsOnce(
            target,
            ".o-dashboard-column",
            "The display layout is force to 1 column"
        );
        assert.containsN(
            target,
            ".o-dashboard-action",
            2,
            "The display should contains the 2 actions"
        );
=======
            };
        },
    });

    QUnit.test("can't switch views in the dashboard", async function (assert) {
        assert.expect(3);

        var target = await createView({
            View: BoardView,
            model: "board",
            data: this.data,
            arch: `<form string="My Dashboard">
                <board style="2-1">
                    <column>
                        <action context="{}" domain="[]" view_mode="list" string="ABC" name="51"/>
                    </column>
                </board>
            </form>`,
            mockRPC: function (route) {
                if (route === "/web/action/load") {
                    return Promise.resolve({
                        res_model: "partner",
                        views: [
                            [4, "list"],
                            [5, "form"],
                        ],
                    });
                }
                return this._super.apply(this, arguments);
            },
            archs: {
                "partner,4,list": `<tree string="Partner"><field name="foo"/></tree>`,
            },
        });

        assert.containsNone(target, ".oe_dashboard_links", "Couldn't allow user to Change layout");
        assert.containsOnce(target, ".oe_dashboard_layout_1", "The display layout is force to 1");
        assert.containsNone(
            target,
            ".o_action .o_control_panel",
            "views in the dashboard do not have a control panel"
        );

        target.destroy();
    });

    QUnit.test("Correctly soft switch to '1' layout on small screen", async function (assert) {
        assert.expect(2);

        var target = await createView({
            View: BoardView,
            model: "board",
            data: this.data,
            arch: `<form>
                <board style="2-1">
                        <column>
                            <action context="{}" domain="[]" view_mode="list" string="ABC" name="51"/>
                        </column>
                        <column>
                            <action context="{}" domain="[]" view_mode="list" string="ABC" name="51"/>
                        </column>
                    </board>
            </form>`,
            mockRPC: function (route) {
                if (route === "/web/action/load") {
                    return Promise.resolve({
                        res_model: "partner",
                        views: [
                            [4, "list"],
                            [5, "form"],
                        ],
                    });
                }
                return this._super.apply(this, arguments);
            },
            archs: {
                "partner,4,list": '<tree string="Partner"><field name="foo"/></tree>',
            },
        });

        assert.containsOnce(target, ".oe_dashboard_layout_1", "The display layout is force to 1");
        assert.containsN(target, ".oe_action", 2, "The display should contains the 2 actions");

        target.destroy();
    });

    QUnit.test("empty board view", async function (assert) {
        assert.expect(2);
        const target = await createView({
            View: BoardView,
            debug: 1,
            model: "board",
            data: this.data,
            arch: `<form string="My Dashboard">
                <board style="2-1">
                    <column/>
                </board>
            </form>`,
            archs: {
                "partner,4,list": '<tree string="Partner"><field name="foo"/></tree>',
            },
        });

        assert.hasClass(
            target.renderer.$el,
            "o_dashboard",
            "with a dashboard, the renderer should have the proper css class"
        );
        assert.containsOnce(
            target,
            ".o_dashboard .o_view_nocontent",
            "should have a no content helper"
        );

        target.destroy();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    });
});

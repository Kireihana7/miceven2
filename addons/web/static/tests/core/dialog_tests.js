/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { uiService } from "@web/core/ui/ui_service";
import { hotkeyService } from "@web/core/hotkeys/hotkey_service";
import { Dialog } from "@web/core/dialog/dialog";
import { makeTestEnv } from "../helpers/mock_env";
import { click, destroy, getFixture, mount } from "../helpers/utils";
import { makeFakeDialogService } from "../helpers/mock_services";

import { Component, useState, onMounted, xml } from "@odoo/owl";
const serviceRegistry = registry.category("services");
let parent;
let target;

async function makeDialogTestEnv() {
    const env = await makeTestEnv();
    env.dialogData = {
        isActive: true,
        close: () => {},
    };
    return env;
}

QUnit.module("Components", (hooks) => {
    hooks.beforeEach(async () => {
        target = getFixture();
        serviceRegistry.add("hotkey", hotkeyService);
        serviceRegistry.add("ui", uiService);
        serviceRegistry.add("dialog", makeFakeDialogService());
    });
    hooks.afterEach(() => {
        if (parent) {
            parent = undefined;
        }
    });

    QUnit.module("Dialog");

    QUnit.test("simple rendering", async function (assert) {
        assert.expect(8);
        class Parent extends Component {}
        Parent.components = { Dialog };
        Parent.template = xml`
            <Dialog title="'Wow(l) Effect'">
                Hello!
            </Dialog>
            `;

        const env = await makeDialogTestEnv();
        parent = await mount(Parent, target, { env });
        assert.containsOnce(target, ".o_dialog");
        assert.containsOnce(
            target,
            ".o_dialog header .modal-title",
            "the header is rendered by default"
        );
        assert.strictEqual(
            target.querySelector("header .modal-title").textContent,
            "Wow(l) Effect"
        );
        assert.containsOnce(target, ".o_dialog main", "a dialog has always a main node");
        assert.strictEqual(target.querySelector("main").textContent, " Hello! ");
        assert.containsOnce(target, ".o_dialog footer", "the footer is rendered by default");
        assert.containsOnce(
            target,
            ".o_dialog footer button",
            "the footer is rendered with a single button 'Ok' by default"
        );
        assert.strictEqual(target.querySelector("footer button").textContent, "Ok");
    });

    QUnit.test("simple rendering with two dialogs", async function (assert) {
        assert.expect(3);
        class Parent extends Component {}
        Parent.template = xml`
              <div>
                  <Dialog title="'First Title'">
                      Hello!
                  </Dialog>
                  <Dialog title="'Second Title'">
                      Hello again!
                  </Dialog>
              </div>
          `;
        Parent.components = { Dialog };
        const env = await makeDialogTestEnv();
        parent = await mount(Parent, target, { env });
        assert.containsN(target, ".o_dialog", 2);
        assert.deepEqual(
            [...target.querySelectorAll("header .modal-title")].map((el) => el.textContent),
            ["First Title", "Second Title"]
        );
        assert.deepEqual(
            [...target.querySelectorAll(".o_dialog .modal-body")].map((el) => el.textContent),
            [" Hello! ", " Hello again! "]
        );
    });

<<<<<<< HEAD
    QUnit.test("click on the button x triggers the service close", async function (assert) {
=======
    QUnit.test("click twice on 'Ok' button of a confirm dialog", async function (assert) {
        assert.expect(5);

        var testPromise = testUtils.makeTestPromise();
        var parent = await createEmptyParent();
        var options = {
            confirm_callback: () => {
                assert.step("confirm");
                return testPromise;
            },
        };
        Dialog.confirm(parent, "", options);
        await testUtils.nextTick();

        assert.verifySteps([]);

        await testUtils.dom.click($('.modal[role="dialog"] .btn-primary'));
        await testUtils.dom.click($('.modal[role="dialog"] .btn-primary'));
        await testUtils.nextTick();
        assert.verifySteps(['confirm']);
        assert.ok($('.modal[role="dialog"]').hasClass('show'), "Should still be opened");
        testPromise.resolve();
        await testUtils.nextTick();
        assert.notOk($('.modal[role="dialog"]').hasClass('show'), "Should now be closed");

        parent.destroy();
    });

    QUnit.test("click on 'Cancel' and then 'Ok' in a confirm dialog", async function (assert) {
        assert.expect(3);

        var parent = await createEmptyParent();
        var options = {
            confirm_callback: () => {
                throw new Error("should not be called");
            },
            cancel_callback: () => {
                assert.step("cancel");
            }
        };
        Dialog.confirm(parent, "", options);
        await testUtils.nextTick();

        assert.verifySteps([]);

        testUtils.dom.click($('.modal[role="dialog"] footer button:not(.btn-primary)'));
        testUtils.dom.click($('.modal[role="dialog"] footer .btn-primary'));
        assert.verifySteps(['cancel']);

        parent.destroy();
    });

    QUnit.test("click on 'Cancel' and then 'Ok' in a confirm dialog (no cancel callback)", async function (assert) {
        assert.expect(2);

        var parent = await createEmptyParent();
        var options = {
            confirm_callback: () => {
                throw new Error("should not be called");
            },
            // Cannot add a step in cancel_callback, that's the point of this
            // test, we'll rely on checking the Dialog is opened then closed
            // without a crash.
        };
        Dialog.confirm(parent, "", options);
        await testUtils.nextTick();

        assert.ok($('.modal[role="dialog"]').hasClass('show'));
        testUtils.dom.click($('.modal[role="dialog"] footer button:not(.btn-primary)'));
        testUtils.dom.click($('.modal[role="dialog"] footer .btn-primary'));
        await testUtils.nextTick();
        assert.notOk($('.modal[role="dialog"]').hasClass('show'));

        parent.destroy();
    });

    QUnit.test("Confirm dialog callbacks properly handle rejections", async function (assert) {
        assert.expect(5);

        var parent = await createEmptyParent();
        var options = {
            confirm_callback: () => {
                assert.step("confirm");
                return Promise.reject();
            },
            cancel_callback: () => {
                assert.step("cancel");
                return $.Deferred().reject(); // Test jquery deferred too
            }
        };
        Dialog.confirm(parent, "", options);
        await testUtils.nextTick();

        assert.verifySteps([]);
        testUtils.dom.click($('.modal[role="dialog"] footer button:not(.btn-primary)'));
        await testUtils.nextTick();
        testUtils.dom.click($('.modal[role="dialog"] footer .btn-primary'));
        await testUtils.nextTick();
        testUtils.dom.click($('.modal[role="dialog"] footer button:not(.btn-primary)'));
        assert.verifySteps(['cancel', 'confirm', 'cancel']);

        parent.destroy();
    });

    QUnit.test("Properly can rely on the this in confirm and cancel callbacks of confirm dialog", async function (assert) {
        assert.expect(2);

        let dialogInstance = null;
        var parent = await createEmptyParent();
        var options = {
            confirm_callback: function () {
                assert.equal(this, dialogInstance, "'this' is properly a reference to the dialog instance");
                return Promise.reject();
            },
            cancel_callback: function () {
                assert.equal(this, dialogInstance, "'this' is properly a reference to the dialog instance");
                return Promise.reject();
            }
        };
        dialogInstance = Dialog.confirm(parent, "", options);
        await testUtils.nextTick();

        testUtils.dom.click($('.modal[role="dialog"] footer button:not(.btn-primary)'));
        await testUtils.nextTick();
        testUtils.dom.click($('.modal[role="dialog"] footer .btn-primary'));

        parent.destroy();
    });

    QUnit.test("Confirm dialog callbacks can return anything without crash", async function (assert) {
        assert.expect(3);
        // Note that this test could be removed in master if the related code
        // is reworked. This only prevents a stable fix to break this again by
        // relying on the fact what is returned by those callbacks are undefined
        // or promises.

        var parent = await createEmptyParent();
        var options = {
            confirm_callback: () => {
                assert.step("confirm");
                return 5;
            },
        };
        Dialog.confirm(parent, "", options);
        await testUtils.nextTick();

        assert.verifySteps([]);
        testUtils.dom.click($('.modal[role="dialog"] footer .btn-primary'));
        assert.verifySteps(['confirm']);

        parent.destroy();
    });

    QUnit.test("Closing alert dialog without using buttons calls confirm callback", async function (assert) {
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        assert.expect(3);
        const env = await makeDialogTestEnv();
        env.dialogData.close = () => assert.step("close");

        class Parent extends Component {}
        Parent.template = xml`
            <Dialog>
                Hello!
            </Dialog>
        `;
        Parent.components = { Dialog };
        parent = await mount(Parent, target, { env });
        assert.containsOnce(target, ".o_dialog");
        await click(target, ".o_dialog header button.btn-close");
        assert.verifySteps(["close"]);
    });

    QUnit.test(
        "click on the default footer button triggers the service close",
        async function (assert) {
            const env = await makeDialogTestEnv();
            env.dialogData.close = () => assert.step("close");
            assert.expect(3);
            class Parent extends Component {}

            Parent.template = xml`
                <Dialog>
                    Hello!
                </Dialog>
            `;
            Parent.components = { Dialog };
            parent = await mount(Parent, target, { env });
            assert.containsOnce(target, ".o_dialog");
            await click(target, ".o_dialog footer button");
            assert.verifySteps(["close"]);
        }
    );

    QUnit.test("render custom footer buttons is possible", async function (assert) {
        assert.expect(2);
        class SimpleButtonsDialog extends Component {}
        SimpleButtonsDialog.components = { Dialog };
        SimpleButtonsDialog.template = xml`
            <Dialog>
                content
                <t t-set-slot="footer">
                    <div>
                        <button class="btn btn-primary">The First Button</button>
                        <button class="btn btn-primary">The Second Button</button>
                    </div>
                </t>
            </Dialog>
          `;
        class Parent extends Component {
            setup() {
                super.setup();
                this.state = useState({
                    displayDialog: true,
                });
            }
        }
        Parent.template = xml`
              <div>
                  <SimpleButtonsDialog/>
              </div>
          `;
        Parent.components = { SimpleButtonsDialog };
        const env = await makeDialogTestEnv();
        parent = await mount(Parent, target, { env });
        assert.containsOnce(target, ".o_dialog");
        assert.containsN(target, ".o_dialog footer button", 2);
    });

    QUnit.test("embed an arbitrary component in a dialog is possible", async function (assert) {
        assert.expect(6);
        class SubComponent extends Component {
            _onClick() {
                assert.step("subcomponent-clicked");
                this.props.onClicked();
            }
        }
        SubComponent.template = xml`
              <div class="o_subcomponent" t-esc="props.text" t-on-click="_onClick"/>
          `;
        class Parent extends Component {
            _onSubcomponentClicked() {
                assert.step("message received by parent");
            }
        }
        Parent.components = { Dialog, SubComponent };
        Parent.template = xml`
              <Dialog>
                  <SubComponent text="'Wow(l) Effect'" onClicked="_onSubcomponentClicked"/>
              </Dialog>
          `;
        const env = await makeDialogTestEnv();
        parent = await mount(Parent, target, { env });
        assert.containsOnce(target, ".o_dialog");
        assert.containsOnce(target, ".o_dialog main .o_subcomponent");
        assert.strictEqual(target.querySelector(".o_subcomponent").textContent, "Wow(l) Effect");
        await click(target.querySelector(".o_subcomponent"));
        assert.verifySteps(["subcomponent-clicked", "message received by parent"]);
    });

    QUnit.test("dialog without header/footer", async function (assert) {
        assert.expect(4);
        class Parent extends Component {}
        Parent.template = xml`
              <Dialog header="false" footer="false">content</Dialog>
          `;
        const env = await makeDialogTestEnv();
        Parent.components = { Dialog };
        parent = await mount(Parent, target, { env });
        assert.containsOnce(target, ".o_dialog");
        assert.containsNone(target, ".o_dialog header");
        assert.containsOnce(target, "main", "a dialog has always a main node");
        assert.containsNone(target, ".o_dialog footer");
    });

    QUnit.test("dialog size can be chosen", async function (assert) {
        assert.expect(5);
        class Parent extends Component {}
        Parent.template = xml`
      <div>
        <Dialog contentClass="'xl'" size="'xl'">content</Dialog>
        <Dialog contentClass="'lg'">content</Dialog>
        <Dialog contentClass="'md'" size="'md'">content</Dialog>
        <Dialog contentClass="'sm'" size="'sm'">content</Dialog>
      </div>`;
        Parent.components = { Dialog };
        const env = await makeDialogTestEnv();
        parent = await mount(Parent, target, { env });
        assert.containsN(target, ".o_dialog", 4);
        assert.containsOnce(
            target,
            target.querySelectorAll(".o_dialog .modal-dialog.modal-xl .xl")
        );
        assert.containsOnce(
            target,
            target.querySelectorAll(".o_dialog .modal-dialog.modal-lg .lg")
        );
        assert.containsOnce(
            target,
            target.querySelectorAll(".o_dialog .modal-dialog.modal-md .md")
        );
        assert.containsOnce(
            target,
            target.querySelectorAll(".o_dialog .modal-dialog.modal-sm .sm")
        );
    });

    QUnit.test("dialog can be rendered on fullscreen", async function (assert) {
        assert.expect(2);
        class Parent extends Component {}
        Parent.template = xml`
            <Dialog fullscreen="true">content</Dialog>
          `;
        Parent.components = { Dialog };
        const env = await makeDialogTestEnv();
        parent = await mount(Parent, target, { env });
        assert.containsOnce(target, ".o_dialog");
        assert.hasClass(target.querySelector(".o_dialog .modal"), "o_modal_full");
    });

    QUnit.test("can be the UI active element", async function (assert) {
        assert.expect(4);
        class Parent extends Component {
            setup() {
                this.ui = useService("ui");
                assert.strictEqual(
                    this.ui.activeElement,
                    document,
                    "UI active element should be the default (document) as Parent is not mounted yet"
                );
                onMounted(() => {
                    assert.containsOnce(target, ".modal");
                    assert.strictEqual(
                        this.ui.activeElement,
                        target.querySelector(".modal"),
                        "UI active element should be the dialog modal"
                    );
                });
            }
        }
        const env = await makeDialogTestEnv();
        Parent.template = xml`<Dialog>content</Dialog>`;
        Parent.components = { Dialog };

        const parent = await mount(Parent, target, { env });
        destroy(parent);

        assert.strictEqual(
            env.services.ui.activeElement,
            document,
            "UI owner should be reset to the default (document)"
        );
    });

    QUnit.test("Ensure on_attach_callback and on_detach_callback are properly called", async function (assert) {
        assert.expect(4);

        const TestDialog = Dialog.extend({
            on_attach_callback() {
                assert.step('on_attach_callback');
            },
            on_detach_callback() {
                assert.step('on_detach_callback');
            },
        });

        const parent = await createEmptyParent();
        const dialog = new TestDialog(parent, {
            buttons: [
                {
                    text: "Close",
                    classes: 'btn-primary',
                    close: true,
                },
            ],
            $content: $('<main/>'),
        }).open();

        await dialog.opened();

        assert.verifySteps(['on_attach_callback']);

        await testUtils.dom.click($('.modal[role="dialog"] .btn-primary'));
        assert.verifySteps(['on_detach_callback']);

        parent.destroy();
    });

    QUnit.test("Should not be displayed if parent is destroyed while dialog is being opened", async function (assert) {
        assert.expect(1);
        const parent = await createEmptyParent();
        const dialog = new Dialog(parent);
        dialog.open();
        parent.destroy();
        await testUtils.nextTick();
        assert.containsNone(document.body, ".modal[role='dialog']");
    });
});

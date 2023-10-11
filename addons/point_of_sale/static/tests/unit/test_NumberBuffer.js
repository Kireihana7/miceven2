odoo.define('point_of_sale.tests.NumberBuffer', function(require) {
    'use strict';

<<<<<<< HEAD
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const makeTestEnvironment = require('web.test_env');
    const testUtils = require('web.test_utils');
    const { mount } = require('@web/../tests/helpers/utils');
    const { LegacyComponent } = require("@web/legacy/legacy_component");

    const { useState, xml } = owl;
=======
    const { Component, useState } = owl;
    const { xml } = owl.tags;
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const makeTestEnvironment = require('web.test_env');
    const testUtils = require('web.test_utils');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    QUnit.module('unit tests for NumberBuffer', {
        before() {},
    });

    QUnit.test('simple fast inputs with capture in between', async function(assert) {
        assert.expect(3);
<<<<<<< HEAD
        const target = testUtils.prepareTarget();
        const env = makeTestEnvironment();

        class Root extends LegacyComponent {
            setup() {
=======

        class Root extends Component {
            constructor() {
                super();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                this.state = useState({ buffer: '' });
                NumberBuffer.activate();
                NumberBuffer.use({
                    nonKeyboardInputEvent: 'numpad-click-input',
                    state: this.state,
                });
            }
            resetBuffer() {
                NumberBuffer.capture();
                NumberBuffer.reset();
            }
<<<<<<< HEAD
            onClickOne() {
                this.trigger('numpad-click-input', { key: '1' });
            }
            onClickTwo() {
                this.trigger('numpad-click-input', { key: '2' });
            }
        }
        Root.template = xml/* html */ `
            <div>
                <p><t t-esc="state.buffer" /></p>
                <button class="one" t-on-click="onClickOne">1</button>
                <button class="two" t-on-click="onClickTwo">2</button>
=======
        }
        Root.env = makeTestEnvironment();
        Root.template = xml/* html */ `
            <div>
                <p><t t-esc="state.buffer" /></p>
                <button class="one" t-on-click="trigger('numpad-click-input', { key: '1' })">1</button>
                <button class="two" t-on-click="trigger('numpad-click-input', { key: '2' })">2</button>
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                <button class="reset" t-on-click="resetBuffer">reset</button>
            </div>
        `;

<<<<<<< HEAD
        await mount(Root, target, { env });

        const oneButton = target.querySelector('button.one');
        const twoButton = target.querySelector('button.two');
        const resetButton = target.querySelector('button.reset');
        const bufferEl = target.querySelector('p');
=======
        const root = new Root();
        await root.mount(testUtils.prepareTarget());

        const oneButton = root.el.querySelector('button.one');
        const twoButton = root.el.querySelector('button.two');
        const resetButton = root.el.querySelector('button.reset');
        const bufferEl = root.el.querySelector('p');
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

        testUtils.dom.click(oneButton);
        testUtils.dom.click(twoButton);
        await testUtils.nextTick();
        assert.strictEqual(bufferEl.textContent, '12');
        testUtils.dom.click(resetButton);
        await testUtils.nextTick();
        assert.strictEqual(bufferEl.textContent, '');
        testUtils.dom.click(twoButton);
        testUtils.dom.click(oneButton);
        await testUtils.nextTick();
        assert.strictEqual(bufferEl.textContent, '21');
<<<<<<< HEAD
=======

        root.unmount();
        root.destroy();
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    });
});

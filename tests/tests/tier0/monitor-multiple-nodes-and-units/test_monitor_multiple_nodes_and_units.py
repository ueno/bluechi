# SPDX-License-Identifier: LGPL-2.1-or-later

import os
from typing import Dict

from bluechi_test.config import BluechiControllerConfig, BluechiAgentConfig
from bluechi_test.machine import BluechiControllerMachine, BluechiAgentMachine
from bluechi_test.service import SimpleService
from bluechi_test.test import BluechiTest

node_name_foo = "node-foo"
node_name_bar = "node-bar"


def exec(ctrl: BluechiControllerMachine, nodes: Dict[str, BluechiAgentMachine]):
    service1 = SimpleService()
    service2 = SimpleService("also-simple.service")
    nodes[node_name_foo].install_systemd_service(service1)
    assert nodes[node_name_foo].wait_for_unit_state_to_be(service1.name, "inactive")

    nodes[node_name_foo].install_systemd_service(service2)
    assert nodes[node_name_foo].wait_for_unit_state_to_be(service2.name, "inactive")

    nodes[node_name_bar].install_systemd_service(service1)
    assert nodes[node_name_bar].wait_for_unit_state_to_be(service1.name, "inactive")

    result, output = ctrl.run_python(os.path.join("python", "monitor.py"))
    if result != 0:
        raise Exception(output)


def test_monitor_specific_node_and_unit(
        bluechi_test: BluechiTest,
        bluechi_ctrl_default_config: BluechiControllerConfig,
        bluechi_node_default_config: BluechiAgentConfig):

    node_foo_config = bluechi_node_default_config.deep_copy()
    node_bar_config = bluechi_node_default_config.deep_copy()

    node_foo_config.node_name = node_name_foo
    node_bar_config.node_name = node_name_bar
    bluechi_ctrl_default_config.allowed_node_names = [node_foo_config.node_name, node_bar_config.node_name]

    bluechi_test.set_bluechi_controller_config(bluechi_ctrl_default_config)
    bluechi_test.add_bluechi_agent_config(node_foo_config)
    bluechi_test.add_bluechi_agent_config(node_bar_config)

    bluechi_test.run(exec)

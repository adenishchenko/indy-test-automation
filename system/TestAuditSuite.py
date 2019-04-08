import pytest
from system.utils import *


@pytest.mark.usefixtures('docker_setup_and_teardown')
class TestAuditSuite:

    @pytest.mark.asyncio
    async def test_case_restart_one_node(self, pool_handler, wallet_handler, get_default_trustee):
        trustee_did, _ = get_default_trustee
        hosts = [testinfra.get_host('ssh://node{}'.format(i)) for i in range(1, 8)]
        for i in range(15):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        output = hosts[5].check_output('systemctl restart indy-node')
        print(output)
        for i in range(30):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        time.sleep(30)
        check_ledger_sync()
        primary1, alias, target_did = await get_primary(pool_handler, wallet_handler, trustee_did)
        output = testinfra.get_host('ssh://node{}'.format(primary1)).check_output('systemctl stop indy-node')
        print(output)
        time.sleep(60)
        for i in range(15):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        output = hosts[5].check_output('systemctl restart indy-node')
        print(output)
        for i in range(30):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        output = testinfra.get_host('ssh://node{}'.format(primary1)).check_output('systemctl start indy-node')
        print(output)
        primary2, alias, target_did = await get_primary(pool_handler, wallet_handler, trustee_did)
        output = testinfra.get_host('ssh://node{}'.format(primary2)).check_output('systemctl stop indy-node')
        print(output)
        time.sleep(60)
        output = hosts[5].check_output('systemctl stop indy-node')
        print(output)
        output = testinfra.get_host('ssh://node{}'.format(primary2)).check_output('systemctl start indy-node')
        print(output)
        for i in range(15):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        output = hosts[5].check_output('systemctl start indy-node')
        print(output)
        for i in range(30):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        time.sleep(30)
        check_ledger_sync()
        await send_and_get_nym(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0])

    @pytest.mark.parametrize('node_num_shift', [0, 1, 5])
    @pytest.mark.asyncio
    async def test_case_restart_master_backup_non_primary(self, pool_handler, wallet_handler, get_default_trustee,
                                                          node_num_shift):
        trustee_did, _ = get_default_trustee
        primary1, alias, target_did = await get_primary(pool_handler, wallet_handler, trustee_did)
        output = testinfra.get_host('ssh://node{}'.format(primary1)).check_output('systemctl stop indy-node')
        print(output)
        time.sleep(60)
        for i in range(15):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        output = testinfra.get_host('ssh://node{}'.format(primary1)).check_output('systemctl start indy-node')
        print(output)
        primary2, alias, target_did = await get_primary(pool_handler, wallet_handler, trustee_did)
        output = testinfra.get_host('ssh://node{}'.format(int(primary2)+node_num_shift))\
            .check_output('systemctl restart indy-node')
        print(output)
        time.sleep(60)
        for i in range(30):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        time.sleep(30)
        check_ledger_sync()
        await send_and_get_nym(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0])

    @pytest.mark.asyncio
    async def test_case_restart_all_nodes_at_the_same_time(self, pool_handler, wallet_handler, get_default_trustee):
        trustee_did, _ = get_default_trustee
        hosts = [testinfra.get_host('ssh://node{}'.format(i)) for i in range(1, 8)]
        primary1, alias, target_did = await get_primary(pool_handler, wallet_handler, trustee_did)
        output = testinfra.get_host('ssh://node{}'.format(primary1)).check_output('systemctl stop indy-node')
        print(output)
        time.sleep(60)
        for i in range(15):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        output = testinfra.get_host('ssh://node{}'.format(primary1)).check_output('systemctl start indy-node')
        print(output)
        outputs = [host.check_output('systemctl restart indy-node') for host in hosts]
        print(outputs)
        time.sleep(30)
        for i in range(30):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        time.sleep(30)
        check_ledger_sync()
        await send_and_get_nym(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0])

    @pytest.mark.asyncio
    async def test_case_restart_f_nodes(self, pool_handler, wallet_handler, get_default_trustee):
        trustee_did, _ = get_default_trustee
        hosts = [testinfra.get_host('ssh://node{}'.format(i)) for i in range(1, 8)]
        primary1, alias, target_did = await get_primary(pool_handler, wallet_handler, trustee_did)
        output = testinfra.get_host('ssh://node{}'.format(primary1)).check_output('systemctl stop indy-node')
        print(output)
        time.sleep(60)
        for i in range(15):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        output = testinfra.get_host('ssh://node{}'.format(primary1)).check_output('systemctl start indy-node')
        print(output)
        outputs = [host.check_output('systemctl restart indy-node') for host in hosts[5:]]
        print(outputs)
        time.sleep(30)
        for i in range(30):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        time.sleep(30)
        check_ledger_sync()
        await send_and_get_nym(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0])

    @pytest.mark.asyncio
    async def test_case_5_restart_n_minus_f_minus_one_nodes(self, pool_handler, wallet_handler, get_default_trustee):
        trustee_did, _ = get_default_trustee
        hosts = [testinfra.get_host('ssh://node{}'.format(i)) for i in range(1, 8)]
        primary1, alias, target_did = await get_primary(pool_handler, wallet_handler, trustee_did)
        output = testinfra.get_host('ssh://node{}'.format(primary1)).check_output('systemctl stop indy-node')
        print(output)
        time.sleep(60)
        for i in range(15):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        output = testinfra.get_host('ssh://node{}'.format(primary1)).check_output('systemctl start indy-node')
        print(output)
        outputs = [host.check_output('systemctl restart indy-node') for host in hosts[3:]]
        print(outputs)
        time.sleep(30)
        for i in range(30):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        time.sleep(30)
        check_ledger_sync()
        await send_and_get_nym(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0])

    @pytest.mark.asyncio
    async def test_case_restart_all_nodes_one_by_one(self, pool_handler, wallet_handler, get_default_trustee):
        trustee_did, _ = get_default_trustee
        hosts = [testinfra.get_host('ssh://node{}'.format(i)) for i in range(1, 8)]
        primary1, alias, target_did = await get_primary(pool_handler, wallet_handler, trustee_did)
        output = testinfra.get_host('ssh://node{}'.format(primary1)).check_output('systemctl stop indy-node')
        print(output)
        time.sleep(60)
        for i in range(15):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        output = testinfra.get_host('ssh://node{}'.format(primary1)).check_output('systemctl start indy-node')
        print(output)
        for host in hosts:
            output = host.check_output('systemctl restart indy-node')
            print(output)
            time.sleep(10)
        time.sleep(30)
        for i in range(30):
            await nym_helper(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0], None, None, None)
        time.sleep(30)
        check_ledger_sync()
        await send_and_get_nym(pool_handler, wallet_handler, trustee_did, random_did_and_json()[0])

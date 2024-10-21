import asyncio

from loguru import logger
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction, Instruction, AccountMeta
from solana.rpc import commitment
from solana.rpc.types import Pubkey
from solders import compute_budget
from solders.token import associated
from solders.keypair import Keypair


class Duck:
    def __init__(self, private_key):
        self.keypair = Keypair.from_base58_string(private_key)
        self.sol_client = AsyncClient("https://cold-hanni-fast-mainnet.helius-rpc.com")

    async def mint(self):
        try:
            logger.info('start mint ……')
            program_id = Pubkey.from_string('pvwX4B67eRRjBGQ4jJUtiUJEFQbR4bvG6Wbe6mkCjtt')
            token_id = Pubkey.from_string('4ALKS249vAS3WSCUxXtHJVZN753kZV6ucEQC41421Rka')
            config_id = Pubkey.from_string('B4cAqfPKtzsqm5mxDk4JkbvPPJoKyXNMyzj5X8SMfdQn')
            instruction_sysvar = Pubkey.from_string('Sysvar1nstructions1111111111111111111111111')
            associated_token_program = Pubkey.from_string('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL')
            token_program = Pubkey.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
            system_program = Pubkey.from_string('11111111111111111111111111111111')
            rent = Pubkey.from_string('SysvarRent111111111111111111111111111111111')

            user_state_seeds = [b'user_state', self.keypair.pubkey().__bytes__()]
            user_state = Pubkey.find_program_address(user_state_seeds, program_id)[0]

            user_ata = associated.get_associated_token_address(self.keypair.pubkey(), token_id)

            config_seeds = [b'config', config_id.__bytes__()]
            config = Pubkey.find_program_address(config_seeds, program_id)[0]

            mint_authority_seeds = [b'mint_authority', config.__bytes__()]
            mint_authority = Pubkey.find_program_address(mint_authority_seeds, program_id)[0]

            recent_blockhash = await self.sol_client.get_latest_blockhash(commitment=commitment.Confirmed)
            transaction = Transaction(recent_blockhash=recent_blockhash.value.blockhash, fee_payer=self.keypair.pubkey())

            priority_fee = compute_budget.set_compute_unit_price(int(PriorityFee * 1e9))
            transaction.add(priority_fee)

            transaction.add(Instruction(
                program_id=program_id,
                accounts=[
                    AccountMeta(pubkey=token_id, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=config, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=user_ata, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=user_state, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True),
                    AccountMeta(pubkey=mint_authority, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=instruction_sysvar, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=associated_token_program, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=token_program, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=system_program, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=rent, is_signer=False, is_writable=False)
                ],
                data=bytes.fromhex('3b8418f67a2708f3')
            ))

            signature = await self.sol_client.send_transaction(transaction, self.keypair)

            resp = await self.sol_client.confirm_transaction(signature.value, commitment=commitment.Confirmed)
            if resp.value[0].err is None:
                logger.success("mint success")
                return True
        except Exception as e:
            logger.error(f"mint failed: {e}")


async def main(private_key):
    duck = Duck(private_key)
    mint_times = 200

    while mint_times > 0:
        success = await duck.mint()
        if success:
            mint_times -= 1


if __name__ == '__main__':
    PriorityFee = 0.001
    PrivateKey = ''
    asyncio.run(main(PrivateKey))

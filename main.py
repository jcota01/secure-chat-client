import os
from typing import Tuple, Optional

from Crypto.PublicKey import RSA

from login_ui import LoginWindow
from chat_ui import ChatWindow
from stubs import login
from utils.account import parse_account_file


def main():
    account: Optional[Tuple[str, RSA.RsaKey]] = None

    # try to find login details in local storage
    if os.path.isfile('account'):
        try:
            f = open('account', 'r')
            account = parse_account_file(f.read())
            f.close()
            login(*account)
            # if the server does not raise an exception login was successful
        except BaseException:
            # there was some error with login
            account = None

    if account is None:
        login_window = LoginWindow()
        login_window.mainloop()
        account = login_window.account

    if account is not None:
        chat_window = ChatWindow()
        chat_window.mainloop()



if __name__ == "__main__":
    main()

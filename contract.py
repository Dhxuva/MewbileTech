"""
CSC148, Winter 2024
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call


# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This class is not to be changed or instantiated. It is an Abstract Class.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ A new month has begun corresponding to <month> and <year>.
        This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        DO NOT CHANGE THIS METHOD
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """ A Term Contract for a phone line

    === Public Attributes ===
    start:
         starting date for the contract
    end:
         ending date for the contract
    last_bill_date:
         Keeps track of the last billing date
    remain_free_mins:
         Keeps track of the number of remaining free mins
    """
    end: datetime.date
    last_bill_date: tuple[int, int]
    remaining_free_mins: int

    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        """ Create a new Term Contract with the <start> date, starts as inactive
        """
        super().__init__(start)
        self.end = end

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ A new month has begun corresponding to <month> and <year>.
        This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        self.last_bill_date = (month, year)
        self.bill.set_rates("TERM", TERM_MINS_COST)
        self.remaining_free_mins = TERM_MINS
        self.bill.add_fixed_cost(TERM_MONTHLY_FEE)
        if (self.start.month, self.start.year) == (month, year):
            # added deposit to first month of contract
            self.bill.add_fixed_cost(TERM_DEPOSIT)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        if self.remaining_free_mins < ceil(call.duration / 60.0):
            self.bill.add_billed_minutes(ceil(call.duration / 60.0))
        else:
            used_free_minutes = ceil(call.duration / 60.0)
            self.remaining_free_mins -= ceil(call.duration / 60.0)
            self.bill.add_free_minutes(used_free_minutes)

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        e_m = self.end.month
        e_y = self.end.year
        if self.last_bill_date[0] < e_m and self.last_bill_date[1] == e_y:
            # if the contract end month
            # is greater than billing month and the year is the same
            return self.bill.get_cost()
        elif self.last_bill_date[1] > self.end.year:
            # if the contract end year is less than the billing year
            return self.bill.get_cost()
        elif self.last_bill_date[0] == e_m and self.last_bill_date[1] == e_y:
            # if the contract is fulfilled until the end date
            return TERM_DEPOSIT
        else:
            return -TERM_DEPOSIT - self.bill.get_cost()
            # negative indicates that the company owes the customer


class MTMContract(Contract):
    """ A MTM Contract for a phone line

    === Public Attributes ===
    start:
         start date for the contract
    """

    def __init__(self, start: datetime.date) -> None:
        """ Create a new MTM Contract with the <start> date, starts as inactive
        """
        super().__init__(start)

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ A new month has begun corresponding to <month> and <year>.
        This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        self.bill.set_rates("MTM", MTM_MINS_COST)
        self.bill.add_fixed_cost(MTM_MONTHLY_FEE)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class PrepaidContract(Contract):
    """ A MTM Contract for a phone line

    === Public Attributes ===
    start:
         start date for the contract
    balance:
         amount of money customer prepaid
    """
    balance: int

    def __init__(self, start: datetime.date, balance: int) -> None:
        """ Create a new MTM Contract with the <start> date, starts as inactive
        """
        super().__init__(start)
        self.balance = balance * (-1)

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ A new month has begun corresponding to <month> and <year>.
        This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        self.bill.set_rates("PREPAID", PREPAID_MINS_COST)
        self.bill.add_fixed_cost(self.balance)
        if 0 >= self.balance > -10:  # balance less than 10
            self.bill.add_fixed_cost(25)
            self.balance -= 25

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        if self.balance < 0:  # if positive balance
            return 0
        else:
            return self.balance

# Implement the MTMContract, TermContract, and PrepaidContract


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })

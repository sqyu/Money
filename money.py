import matplotlib.pyplot as plt
import time

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

num_of_dates = {1:31, 2:29, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}

def is_leap_year(year):
    return (not year % 400) or (year % 100 and not year % 4)

def is_date(s, year = 0):
    # year argument has to be given if no year in s; however, it will be overwritten if s does contain a year
    contains_year = len(s.split("/")) == 3 and is_int(s.split("/")[2]) and int(s.split("/")[2]) in range(2015, int(time.strftime("%Y")) + 1) # "date" contains year
    if len(s.split("/")) < 2 or len(s.split("/")) > 3 or (len(s.split("/")) == 3 and not contains_year):
        return False
    assert (contains_year or year != 0)
    m,d = s.split("/")[0:2] # month and date
    if contains_year: # if date contains year
        year = int(s.split("/")[2]) # overwrite year
        return is_date(m + "/" + d, year) # recursive check
    return len(s.split("/")) == 2 and is_int(m + d) and int(m) in range(1,13) and int(d) in range(num_of_dates[int(m)] + 1) and not (not is_leap_year(year) and m == "2" and d == "29")

def next(date, year): # next date of date given year
    assert(is_date(date, year))
    if len(date.split("/")) == 3: # if date contains year
        assert year == int(s.split("/")[2]) # Sanity check
    m, d = map(int, date.split("/")[0:2]) # month and date
    if num_of_dates[m] == d or (m == 2 and d == 28 and not is_leap_year(year)): # if last day of the month
        if m == 12: # if 12/31
            return "1/1"
        return str(m+1) + "/1" # last day of other months
    return str(m) + "/" + str(d+1) # some month

def is_amt(s): # is an amount
    return "$" in s and ((s[0]==("$") and is_float(s[1:])) or ((s[0:2]=="-$" or s[0:2]=="$-") and is_float(s[2:])) or (s[0] == "(" and s[-1] == ")" and ((s[1:3]=="-$" or s[1:3]=="$-") and is_float(s[3:-1]))))

def amt(s): # map to amount
    return (-2*("-" in s) + 1) * float(s.replace("$", "").replace("-", "").replace("(", "").replace(")", ""))

def negative_txn_spent_or_earned(s): # If a txn amount is negative, credited to spent if with parentheses, otherwise counted as earning
    if s[0:2] == "-$" or s[0:2] == "$-":
        return False
    elif s[0:3] == "(-$" or s[0:3] == "($-":
        return True
    else:
        print("Negative transaction amount encountered, but unable to decide if amount spent or earned. Item amount:\n" + s)
        assert False

class biweekly:
    def __init__(self, start_date, start_year):
        self.start_date = start_date
        self.end_date = "NO_END_DATE"
        self.start_year = start_year
        self.end_year = start_year
        self.spent  = 0
        self.earned = 0
    def __str__(self):
        return "Summary: " + self.start_date + "/" + str(self.start_year) + "-" + self.end_date + "/" + str(self.end_year) + " Spent $" + "{0:.2f}".format(self.spent) + ", Earned $" + "{0:.2f}".format(self.earned) + ", Net Earning $" + "{0:.2f}".format(self.earned - self.spent)

def b_sum(biweekly_objects): # print summaries
    print("_" * 69)
    for b in biweekly_objects:
        print(b)
        print("_" * 69)
    starts = []
    spents = []
    earneds = []
    nets = []
    for b in biweekly_objects:
        starts.append(b.start_date + "/" + str(b.start_year))
        spents.append(b.spent)
        earneds.append(b.earned)
        nets.append(b.earned - b.spent)
    print("Balance: " + starts[0] + "-" + biweekly_objects[-1].end_date + "/" + str(biweekly_objects[-1].end_year) + " Spent $" + "{0:.2f}".format(sum(spents)) + ", Earned $" + "{0:.2f}".format(sum(earneds)) + ", Total Earnings $" + "{0:.2f}".format(sum(nets)) + "\n")

    B = len(biweekly_objects)
    colors = ['r', 'g', 'gold']
    labels = ["$ Spent", "$ Earned", "Cum. Net Earnings"]
    fig = plt.figure()
    ax = plt.subplot(111)
    ax.plot(range(B), spents, 'o-', linewidth = 2, color = colors[0], label = labels[0])
    ax.plot(range(B), earneds, 'go--', linewidth = 1.5, color = colors[1], label = labels[1])
    cum_earn = [sum(nets[:(i+1)]) for i in range(B)]
    ax.bar([i-0.3 for i in range(B)], cum_earn, width = 0.6, color = colors[2], edgecolor = 'None', label = labels[2])

    ax.axis([-0.3, B-0.7, 0, (max([0] + spents + cum_earn) + 10) * 1.02])
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    for color, text in zip(colors, ax.legend(loc = 'center left', bbox_to_anchor=(1,0.5)).get_texts()):
        text.set_color(color)

    plt.xlabel("Date mm/dd/yy")
    plt.ylabel("Amount in dollars")
    plt.xticks(range(B), starts)
    plt.title("Biweekly spent amounts")
    plt.show()


if __name__ == '__main__':
    biweekly_objects = []
    mark = 's' # type of next line. 's': start date expected, 'i': 'regular item, could be paycheck'
    current_date = ""
    current_year = 0
    warning = ""
    error = ""

    print("Make sure you obey the following formatting rules:\n")
    print("(1) The file should start with the date of the first transaction including year.")
    print("(2) All dates must have the format m(m)/d(d)(/yyyy)")
    print("(3) Each biweekly period ends with a paycheck.")
    print("(4) After each paycheck, lines with underscores only or beginning with \"Summary:\" are ignored until the next period starts, which must be indicated by a date.")
    print("(5) All regular transactions should start with $ sign, or with -$ or $- and optionally included inside a pair of parenthesis if a cash inflow.")
    print("(6) Lines that do not follow the rules above will be ignored (with warning), or will cause the script to be exited.\n")
    print("Now please input your memo.\n")

    while True:
        new_item = raw_input()
        while new_item == "" or (mark == 's' and set(new_item) == set(['_'])) or new_item.startswith("Summary"):
            # while blank, or waiting for start of biweekly (skip __ and summary between paycheck and next period)
            new_item = raw_input()
        if mark == 's':
            if "Balance" in new_item:
                break
            if not is_date(new_item, current_year): # Sanity check
                error = "First transaction date of the period expected. Observed:\n" + new_item
                break
            if current_date:
                if len(new_item.split("/")) == 3: # If contains year
                    current_year = int(new_item.split("/")[2]) # updates year
                    new_item = "/".join(new_item.split("/")[0:2]) # removes year
                start_date = next(current_date, current_year) # REAL start date of next period
                if start_date == "1/1" and int(new_item.split("/")[0]) == 12: # If start date is 1/1 but first transaction is in previous year, increment current_year by 1
                    current_year += 1
                biweekly_objects.append(biweekly(start_date, int(current_year))) # new biweekly period
                if start_date != new_item: # if start date does not match date of the first transaction
                    warning += "*** Period starts from " + start_date + "/" + str(current_year) + ", but first transaction was on " + new_item + "\n"
            else: # very beginning of the file, HAS TO CONTAIN YEAR
                biweekly_objects.append(biweekly("/".join(new_item.split("/")[0:2]), int(new_item.split("/")[2])))
                current_year = int(new_item.split("/")[2])
                new_item = "/".join(new_item.split("/")[0:2])
            current_date = new_item # finally, update current date
            mark = 'i' # new period started, expect regular items
            continue
        if mark == 'i':
            if "_" in new_item:     # When underscore appears when regular item expected, this indicates the last (incomplete) biweekly period has ended, and the next line should be final summary, so ignore and break
                biweekly_objects[-1].end_date = current_date # update last transaction date (for printing)
                biweekly_objects[-1].end_year = current_year # update last transaction year (for printing)
                warning += "*** Last period ignored: " + str(biweekly_objects.pop())
                _ = raw_input() # Read in last general summary, discard it, and break
                break
            if is_date(new_item, current_year):
                if len(new_item.split("/")) == 3: # If contains year
                    current_year = int(new_item.split("/")[2]) # updates year
                    new_item = "/".join(new_item.split("/")[0:2])
                current_date = new_item # used for closing date
                continue
            if not is_amt(new_item.split(" ")[0]): # if not a transaction, ignore
                warning += "*** Ignored: " + new_item + "\n"
                continue
            # can only be a transaction/earning after this point
            m = amt(new_item.split(" ")[0])
            if "paycheck" in new_item.lower() or "pay check" in new_item.lower(): # if PAYCHECK
                if negative_txn_spent_or_earned(new_item.split(" ")[0]):
                    error = "Paychecks should be earnings, not spendings (no parentheses allowed around earning amounts). Observed:\n" + new_item + "\n"
                    break
                if m >= -900: # paychecks have to be more than $900, hopefully...
                    error = "Expected paycheck, but observed " + new_item + "\n"
                    break
                biweekly_objects[-1].end_date = current_date # closing date for this period
                biweekly_objects[-1].end_year = current_year # clsoing year for this period
                biweekly_objects[-1].earned += -m # earning for this period
                mark = 's'  # wait for start of next period
            else: # regular transaction
                if m > 0 or (m < 0 and negative_txn_spent_or_earned(new_item.split(" ")[0])):
                    biweekly_objects[-1].spent += m
                else:
                    biweekly_objects[-1].earned += -m
    if error:
        print(error)
        quit()

    if warning:
        print(warning)

    b_sum(biweekly_objects) # summary





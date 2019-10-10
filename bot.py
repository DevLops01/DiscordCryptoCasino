import discord
from botSecret import secret
from fetch import *
from data import *
from discord.ext import commands
import random
from collections import namedtuple
import asyncio
import time

# Set coin specific parameters

CoinName = "" # Enter the ticker of the Altcoin 
MaxCoinFlipBet = 10 # Enter the max bet amount for coinflip
MinCoinFlipBet = 1 # Enter the min bet amount for coinflip
MaxBlackJackBet = 10 # Enter the max bet amount for blackjack
MinBlackJackBet = 0.01 # Enter the min bet amount for blackjack
MaxDiceBet = 10 # Enter the max bet amount for dice
MinDiceBet = 0.01 # Enter the min bet amount for dice
LostBetsAddy = "" # Enter the address the client would like lost bets to be sent to
myUid = "" # Enter the account name for the address the client would like to pay out wins from

bot = commands.Bot(command_prefix='$')
bot.remove_command("help")


@bot.event
async def on_ready():
    print("Bot is online!")
    print('Logged in as {0.user}'.format(bot))

@bot.command()
async def help(ctx):
    tuid = "<@" + str(ctx.author.id) + ">"
    await ctx.channel.send(tuid + """
    \n**$create** - Creates a wallet attached to your discord account. 
    \n**$balance** - Check your wallet balance.
    \n**$address** - Returns the users Wallet address.
    \n**$send** - Sends coins to any address. Example: ' $send Cca1eNQMF4JYCjzBsbJBbLLHE2jDPmqzop 1 '
    \n**$coinflip** - Starts a game of coinflip. Example: ' $coinflip 1 Heads ' where 1 is the amount you wish to bet.
    \n**$blackjack** - Starts a game of blackjack. Example: ' $blackjack 10 ' where 10 is the amount you wish to bet.
    \n**$dice** - Starts a game of dice. Example: ' $dice 10 6 ' where 10 is the amount you wish to bet and 6 is the amount to roll under in order to win.
    \n**$payouts** - Returns a list of payouts for Dice depending on what the 'under' is set at.
    """)

@bot.command()
async def payouts(ctx):
    tuid = "<@" + str(ctx.author.id) + ">"
    await ctx.channel.send(tuid + """ 
    ```\n**Dice Payouts:** 
    \nUnder 11 Payout = 1.09 * Bet
    \nUnder 10 Payout = 1.2 * Bet
    \nUnder 9 Payout = 1.33 * Bet
    \nUnder 8 Payout = 1.5 * Bet
    \nUnder 7 Payout = 1.71 * Bet
    \nUnder 6 Payout = 2 * Bet
    \nUnder 5 Payout = 2.4 * Bet
    \nUnder 4 Payout = 3 * Bet
    \nUnder 3 Payout = 4 * Bet
    \nSnake Eyes Payout = 6 * Bet```
    """)

# Create User Wallet
@bot.command()
async def create(ctx):
    c.execute("SELECT * FROM users")
    existingUsers = c.fetchall()
    raw = str(ctx.author.id)
    uid = "<@" + str(ctx.author.id) + ">"
    for i in existingUsers:
        if i[0] == raw:
            botMessage = await ctx.channel.send(uid + " \nYou already have a wallet.")
            time.sleep(5)
            await botMessage.delete()
            await ctx.message.delete()
            return
    else:
        address = getNewAddy(ctx.author.id)
        balance = getBalance(str(ctx.author.id))
        username = str(ctx.author)
        createWallet(raw, username, address, balance)
        print(c.fetchall())
        botMessage = await ctx.channel.send(uid + ' ' + '\n**AltCasino Wallet - ' + CoinName + ' ** \n**Address:** '
                                   + str(address['result']) + '. \n**Balance:** ' + str(balance['result']))
        updateBalances()
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return

# Return User Balance
@bot.command()
async def balance(ctx):
    c.execute("SELECT * FROM users WHERE userid=:uid",
              {'uid': ctx.author.id})
    existingUsers = c.fetchall()
    uid = "<@" + str(ctx.author.id) + ">"
    for i in existingUsers:
        newBalance = i[3]
        botMessage = await ctx.channel.send(uid + ' ' + '\n**AltCasino Wallet - ' + CoinName + '** \n**Balance:** ' + str(newBalance) + ' ' + CoinName)
        updateBalances()
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return
    else:
        botMessage =await ctx.channel.send(uid + "\nYou haven't created a wallet yet. Please use **$create** command.")
        updateBalances()
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return

# Return User Deposit Address
@bot.command()
async def address(ctx):
    updateBalances()
    c.execute("SELECT * FROM users WHERE userid=:uid",
              {'uid': ctx.author.id})
    existingUsers = c.fetchall()
    uid = "<@" + str(ctx.author.id) + ">"
    for i in existingUsers:
        userAddy = i[2]
        print(userAddy)
        botMessage = await ctx.channel.send(uid + '\n**AltCasino Wallet - CPU**' + '\n**Wallet Address:** ' + userAddy)
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return
    else:
        botMessage = await ctx.channel.send(uid + "\nYou haven't created a wallet yet. Please use **$create** command.")
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return

# Send Coins
@bot.command()
async def send(ctx, arg1, arg2):
    tuid = uid = "<@" + str(ctx.author.id) + ">"
    uid = ctx.author.id
    address = arg1
    amount = arg2
    spend = sendCoins(str(uid), str(address), str(amount))
    print(spend)
    
    if str(spend['result']) == "None":
        botMessage = await ctx.channel.send(tuid + "\n**Error:** " + str(spend['error']['message']))
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return
        # await ctx.channel.send(tuid + "\n**Error:** Insufficient Funds")
    
    else:
        botMessage = await ctx.channel.send(tuid + "\nTransaction Successful: \n**TXID:** " + str(spend['result']))
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()

# Start a Game of Coinflip
@bot.command()
async def coinflip(ctx, bet, userChoice):
    updateBalances()
    c.execute("SELECT * FROM users WHERE userid=:uid",
              {'uid': ctx.author.id})
    existingUsers = c.fetchall()
    uid = str(ctx.author.id)
    tuid = "<@" + str(ctx.author.id) + ">"
    
    for i in existingUsers:
        userAddy = i[2]
        toPlay = getBalance(str(ctx.author.id))
        newBalance = toPlay['result']
        
        if newBalance < float(bet):
            botMessage = await ctx.channel.send(tuid + "\nSorry, you don't have that many coins. \n**Balance:** " + str(newBalance) + ' ' + CoinName)
            time.sleep(5)
            await botMessage.delete()
            await ctx.message.delete()
            return
        elif float(bet) > MaxCoinFlipBet:
            botMessage = await ctx.channel.send(tuid + "\nSorry, the max bet for Coinflip is " + str(MaxCoinFlipBet) + ' ' + CoinName)
            time.sleep(5)
            await botMessage.delete()
            await ctx.message.delete()
            return
        elif float(bet) < MinCoinFlipBet:
            botMessage = await ctx.channel.send(tuid + "\nSorry, the minimum bet for Coinflip is " + str(MinCoinFlipBet) + ' ' + CoinName)
            time.sleep(5)
            await botMessage.delete()
            await ctx.message.delete()
            return
        elif newBalance >= float(bet):
            betOn = userChoice.lower()
            Heads = "heads"
            Tails = "tails"
            options = [Heads, Tails]
            landed = random.choice(options)
            
            if landed == betOn:
                botMessage1 = await ctx.channel.send(tuid + "\nCoin landed on **" + landed.upper() + "**" + "\n**Congratulations!** You Won " + str(bet) + ' ' + CoinName)
                sendCoins(myUid, userAddy, bet)
                updateBalances()
                botMessage = await ctx.channel.send("**Please wait 5 seconds before placing a new bet**")
                time.sleep(5)
                await botMessage.delete()
                await botMessage1.delete()
                await ctx.message.delete()
                await ctx.channel.purge(limit=3)
                await ctx.channel.send("**You can now place a new bet**")
                return
            
            elif landed != betOn:
                botMessage1 = await ctx.channel.send(tuid +"\nCoin landed on **" + landed.upper() + "**" + "\n**Oops!** You Lost " + str(bet) + ' ' + CoinName)
                sendCoins(uid, LostBetsAddy, bet)
                updateBalances()
                botMessage = await ctx.channel.send("**Please wait 5 seconds before placing a new bet**")
                time.sleep(5)
                await botMessage.delete()
                await botMessage1.delete()
                await ctx.message.delete()
                await ctx.channel.purge(limit=3)
                await ctx.channel.send("**You can now place a new bet**")
                return
        return
    else:
        botMessage = await ctx.channel.send(tuid + "\nYou haven't created a wallet yet. Please use **$create** command.")
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return
def check(ctx):
    return lambda m: m.author == ctx.author and m.channel == ctx.channel

async def get_input_of_type(func, ctx):
    while True:
        try:
            msg = await bot.wait_for('message', timeout= 30, check=check(ctx))
            return func(msg.content)
        except ValueError:
            continue 

# Start a game of BlackJack
@bot.command()
async def blackjack(ctx, bet):
    toPlay = getBalance(str(ctx.author.id))
    newBalance = toPlay['result']

    tuid = "<@" + str(ctx.author.id) + ">"
    
    if float(bet) > MaxBlackJackBet:
        botMessage = await ctx.channel.send(tuid + "\nSorry, Max bet for Black Jack is " + str(MaxBlackJackBet) )
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return
    
    elif float(bet) < MinBlackJackBet:
        botMessage = await ctx.channel.send(tuid + "\nSorry, Minimum bet for Black Jack is " + str(MaxBlackJackBet) )
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return
     
    if newBalance < float(bet):
        botMessage = await ctx.channel.send(tuid + "\nSorry, you don't have that many coins. \n**Balance:** " 
        + str(newBalance) + ' ' + CoinName)
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return
    
    uid = str(ctx.author.id)
    c.execute("SELECT * FROM users WHERE userid=:uid",
              {'uid': ctx.author.id})
    existingUsers = c.fetchall()
    
    if existingUsers == []:
        botMessage = await ctx.channel.send(tuid + "\nYou haven't created a wallet yet. Please use **$create** command.")
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return
    
    for i in existingUsers:
        userAddy = i[2]
    
    cValue = {'Ace': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6,
              'Seven': 7, 'Eight': 8, 'Nine': 9, 'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10}
    cSuit = {'Hearts': 0, 'Spades': 1, 'Clubs': 2, 'Diamonds': 3}
    deck = [] # Empt Deck Array
    dCards = [] # Empty Dealer Cards Array
    pCards = [] # Empty Player Cards Array

    # Build Deck
    for i in cValue.keys():
        for j in cSuit.keys():
            deck.append(i + ' of ' + j) # Adds 52 cards to the Deck Array 
    
    # Shuffle Deck
    random.shuffle(deck)
    random.shuffle(deck)
    random.shuffle(deck)
    # Dealer Hand

    while len(dCards) != 2:
        dCards.append(random.choice(deck)) # Picks Random Cards from the deck and places them into the Dealers Hand
    
    if len(dCards) == 2:
        dFirstCard = getCardValue(dCards[0])
        dSecondCard = getCardValue(dCards[1])
        dealerTotal = dFirstCard + dSecondCard
    
    while len(pCards) != 2:
        pCards.append(random.choice(deck)) # Picks Random Cards from the deck and places them into the Players Hand
    
    if len(pCards) == 2:
        pFirstCard = getCardValue(pCards[0]) # Returns card's numerical value
        pSecondCard = getCardValue(pCards[1])
        playerTotal = pFirstCard + pSecondCard # Sum of Players first and second card
    # Determine if user wants to Hit or Stay
    if playerTotal < 21:
        botMessage = await ctx.channel.send(tuid + "\nDealer Has **HIDDEN** & " + '**' + dCards[0] + '**' 
        + "\nYou Have " + '**' + str(pCards) + '**' + ' :** ' + str(playerTotal) + '**' 
        + "\n**Stay**: [S] or **Hit**: [H]?")
        stayOrHit = await get_input_of_type(str, ctx)
        
        while stayOrHit.lower() != "h" and stayOrHit.lower() != "s":
            botMessage = await ctx.channel.send(tuid + "\n Please enter **Stay**: [S] or **Hit**: [H]")
            stayOrHit = await get_input_of_type(str, ctx)
           
       
        while stayOrHit.lower() == "h":
            pCards.append(random.choice(deck))
            cardNum = len(pCards)
            cardNum -= 1
            newCard = getCardValue(pCards[cardNum])
            playerTotal += newCard
            botMessage = await ctx.channel.send(tuid + "\nDealer Has **HIDDEN** & " + '**' + dCards[0] + '**'
             + "\nYou Have " + '**' + str(pCards) + '**' + ' : **' + str(playerTotal) + '**' + "\n**Stay**: [S] or **Hit**: [H]?")


           # if Player hit and hasn't busted ask player to Stay or Hit
            if playerTotal <= 21:
                stayOrHit = await get_input_of_type(str, ctx)
                while stayOrHit.lower() != "h" and stayOrHit.lower() != "s":
                    botMessage = await ctx.channel.send(tuid + "\n Please enter **Stay**: [S] or **Hit**: [H]")
                    stayOrHit = await get_input_of_type(str, ctx)
                    


           # Determine if Player Hit and hasn't busted
            elif playerTotal > 21:
                botMessage = await ctx.channel.send(tuid + "\nBust! You Lost " + str(bet) + ' ' + CoinName +  '\nYour Total: **' + str(playerTotal) + '**')
                sendCoins(uid, LostBetsAddy, bet)
                updateBalances()
                botMessage = await ctx.channel.send("**Please wait 5 seconds before placing a new bet**")
                time.sleep(5)
                await botMessage.delete()
                await ctx.message.delete()
                await ctx.channel.purge(limit=10)
                botMessage = await ctx.channel.send("You can now place a new bet.")
                return
        
        # If Decision does not equal hit
        # TODO switch this to a more explicit method, setting it equal to Stay causes random infinite loops
        # It's currently fixed by not allowing input other than stay or hit
        while stayOrHit.lower() != "h": 
    
            # If Dealer hand is less than 16, Dealer draws another card

            if dealerTotal <= 16:
                dCards.append(random.choice(deck))
                DcardNum = len(dCards)
                DcardNum -= 1
                newDCard = getCardValue(dCards[DcardNum])
                dealerTotal += newDCard
             
            
            # Determine if Dealer Hand Busted
            elif dealerTotal > 21:
                botMessage = await ctx.channel.send(tuid + "\nDealer Has " + '**' + str(dCards) + '**'
                    + "\nYou Have " + '**' + str(pCards) + '**' + ' : **' + str(playerTotal) + '**')
                botMessage = await ctx.channel.send(tuid + "\nYou Won! " + str(bet) + ' ' + CoinName +"\nDealer Busted" + '\nYour Total: ' '**' + str(playerTotal) + '** \nDealer Total: **' + str(dealerTotal) + '**')
                sendCoins(myUid, userAddy, bet)
                updateBalances()
                botMessage = await ctx.channel.send("**Please wait 5 seconds before placing a new bet**")
                time.sleep(5)
                await botMessage.delete()
                await ctx.message.delete()
                await ctx.channel.purge(limit=10)
                botMessage = await ctx.channel.send("You can now place a new bet.")
                return
            
            # Determine Winner
            elif dealerTotal > 16 and dealerTotal <= 21:
                if dealerTotal < playerTotal:
                    botMessage = await ctx.channel.send(tuid + "\nDealer Has " + '**' + str(dCards) + '**'
                    + "\nYou Have " + '**' + str(pCards) + '**' + ' : **' + str(playerTotal) + '**')
                    botMessage = await ctx.channel.send(tuid + "\nYou Won! "  + str(bet) + ' ' +CoinName + '\nYour Total: ' '**' + str(playerTotal) + '** \nDealer Total: **' + str(dealerTotal)+ '**')
                    sendCoins(myUid, userAddy, bet)
                    updateBalances()
                    botMessage = await ctx.channel.send("**Please wait 5 seconds before placing a new bet**")
                    time.sleep(5)
                    await botMessage.delete()
                    await ctx.message.delete()
                    await ctx.channel.purge(limit=10)
                    botMessage = await ctx.channel.send("You can now place a new bet.")
                    return
                elif dealerTotal > playerTotal:
                    botMessage = await ctx.channel.send(tuid + "\nDealer Has " + '**' + str(dCards) + '**'
                    + "\nYou Have " + '**' + str(pCards) + '**' + ' : **' + str(playerTotal) + '**')
                    botMessage = await ctx.channel.send(tuid + "\nYou Lost! "  + str(bet) + ' ' +CoinName + '\nYour Total: ' '**' + str(playerTotal) + '** \nDealer Total: **' + str(dealerTotal) + '**')
                    sendCoins(uid, LostBetsAddy, bet)
                    updateBalances()
                    botMessage = await ctx.channel.send("**Please wait 5 seconds before placing a new bet**")
                    time.sleep(5)
                    await botMessage.delete()
                    await ctx.message.delete()
                    await ctx.channel.purge(limit=10)
                    botMessage = await ctx.channel.send("You can now place a new bet.")
                    return
            
            # Determine A Tie
            if playerTotal == dealerTotal and playerTotal <= 21 and dealerTotal <= 21:
                botMessage = await ctx.channel.send(tuid + "\nDealer Has " + '**' + str(dCards) + '**'
                    + "\nYou Have " + '**' + str(pCards) + '**' + ' : **' + str(playerTotal) + '**')
                botMessage = await ctx.channel.send(tuid + "\nTie! No Payout " + '\nYour Total: ' '**' + str(playerTotal) + '** \nDealer Total: **' + str(dealerTotal) + '**')
                updateBalances()
                botMessage = await ctx.channel.send("**Please wait 5 seconds before placing a new bet**")
                time.sleep(5)
                await botMessage.delete()
                await ctx.message.delete()
                await ctx.channel.purge(limit=10)
                botMessage = await ctx.channel.send("You can now place a new bet.")
                return 
         
# Start a game of Dice
@bot.command()
async def dice(ctx, bet, under):
    tuid = "<@" + str(ctx.author.id) + ">"
    uid = str(ctx.author.id)
    c.execute("SELECT * FROM users WHERE userid=:uid",
              {'uid': ctx.author.id})
    existingUsers = c.fetchall()

    if existingUsers == []:
        botMessage = await ctx.channel.send(tuid + "\nYou haven't created a wallet yet. Please use **$create** command.")
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return
    
    toPlay = getBalance(str(ctx.author.id))
    newBalance = toPlay['result']
    
    if newBalance < float(bet):
       botMessage = await ctx.channel.send(tuid + "\nSorry, you don't have that many coins. \n**Balance:** " 
        + str(newBalance) + ' ' + CoinName)
       time.sleep(5)
       await botMessage.delete()
       await ctx.message.delete()
       return
    
    elif float(bet) > MaxDiceBet:
        botMessage = await ctx.channel.send(tuid + "\nSorry, the max bet for Dice is " + str(MaxDiceBet) + ' ' + CoinName)
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return
    elif float(bet) < MinDiceBet:
        botMessage = await ctx.channel.send(tuid + "\nSorry, the minimum bet for Dice is " + str(MinDiceBet) + ' ' + CoinName)
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return
    
    for i in existingUsers:
        userAddy = i[2]
    
    
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    roll = dice1 + dice2
    

    if int(under) == 2:
        payout = float(bet) * 6
    if int(under) == 3:
        payout = float(bet) * 4
    if int(under) == 4:
        payout = float(bet) * 3
    if int(under) == 5:
        payout = float(bet) * 2.4
    if int(under) == 6:
        payout = float(bet) * 2
    if int(under) == 7:
        payout = float(bet) * 1.71
    if int(under) == 8:
        payout = float(bet) * 1.5
    if int(under) == 9:
        payout = float(bet) * 1.33
    if int(under) == 10:
        payout = float(bet) * 1.2
    if int(under) == 11:
        payout = float(bet) * 1.09
    

    elif int(under) > 11:
        botMessage = await ctx.channel.send(tuid + "\nRoll Under value must be less than or equal to 11. ")
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return
    elif int(under) < 2:
        botMessage = await ctx.channel.send(tuid + "\nRoll Under value must be greater than or equal to 3. ")
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        return

    if roll == 2 and int(under) == 2:
        botMessage = await ctx.channel.send(tuid + "\n**Snake Eyes!** \n**You Won " + str(payout) + ' ' +CoinName + '**' +
        "\nDice One: " + str(dice1) + "\nDice Two: " + str(dice2) + "\n**Total:** " + str(roll))
        sendCoins(myUid, userAddy, payout)
        updateBalances()
        botMessage = await ctx.channel.send("**Please wait 5 seconds before placing a new bet**")
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        botMessage = await ctx.channel.send("You can now place a new bet.")
        await ctx.channel.purge(limit=3)
        return

    elif roll < int(under):
        botMessage = await ctx.channel.send(tuid + "\n**You Won " + str(payout) + ' ' +CoinName + '**' +
        "\nDice One: " + str(dice1) + "\nDice Two: " + str(dice2) + "\n**Total:** " + str(roll))
        sendCoins(myUid, userAddy, payout)
        updateBalances()
        botMessage = await ctx.channel.send("**Please wait 5 seconds before placing a new bet**")
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        await ctx.channel.purge(limit=3)
        botMessage = await ctx.channel.send("You can now place a new bet.")
        return
    
    elif roll >= int(under):
        botMessage = await ctx.channel.send(tuid + "\n**You Lost " + str(bet) + ' ' +CoinName + '**' +
        "\nDice One: " + str(dice1) + "\nDice Two: " + str(dice2) + "\n**Total:** " + str(roll))
        sendCoins(uid, LostBetsAddy, bet)
        updateBalances()
        botMessage = await ctx.channel.send("**Please wait 5 seconds before placing a new bet**")
        time.sleep(5)
        await botMessage.delete()
        await ctx.message.delete()
        await ctx.channel.purge(limit=3)
        botMessage = await ctx.channel.send("You can now place a new bet.")
        return

@bot.event
async def on_command_error(error, ctx):
    if error.guild is None:
        return
    else:
        tuid = "<@" + str(error.author.id) + ">"
        botMessage = await error.channel.send(tuid + "\n**Error:** Improper format or command does not exist.\nPlease enter **$help** for a list of available commands.")
        time.sleep(5)
        await botMessage.delete()
        await error.message.delete()

    

bot.run(secret)

"""
Random Client Profile Generator for Project CAII

Generates realistic, randomized client profiles for simulation testing.
"""

import random
from typing import Dict

def generate_random_client_profile() -> str:
    """
    Generates a randomized client profile with 50 simulated email interactions.
    
    Returns:
        String containing 50 email interactions revealing client's financial situation,
        psychology, and needs.
    """
    
    # Random client attributes
    age = random.randint(28, 55)
    salary = random.choice([65000, 75000, 85000, 95000, 110000, 125000, 150000, 180000])
    spouse_salary = random.choice([0, 45000, 55000, 65000, 75000, 85000, 95000])
    has_spouse = spouse_salary > 0
    num_children = random.choice([0, 0, 1, 1, 2, 2, 3]) if age > 25 else 0
    
    house_price = random.choice([0, 350000, 425000, 500000, 650000, 800000])
    mortgage = int(house_price * 0.8) if house_price > 0 else 0
    monthly_mortgage = int(mortgage * 0.005) if mortgage > 0 else 0
    
    savings_401k = random.randint(5000, 80000)
    emergency_fund = random.randint(3000, 25000)
    student_loans = random.choice([0, 0, 12000, 18000, 25000, 35000, 50000])
    car_loan = random.choice([0, 0, 15000, 22000, 28000])
    
    work_life_insurance = salary * 2
    
    skepticism = random.randint(4, 9)
    communication_style = random.choice([
        "analytical and detail-oriented",
        "big-picture focused",
        "emotional and family-centered",
        "research-heavy and skeptical",
        "pragmatic and cost-conscious"
    ])
    
    # Generate email history
    emails = []
    
    # Email 1-5: Initial awareness
    emails.append(f"Email 1 (Client to Self):\nNeed to figure out this life insurance thing. {'Sarah' if has_spouse else 'My family'} has been bugging me about it{'since the baby came' if num_children > 0 else ''}.")
    
    if has_spouse:
        emails.append(f"Email 2 (Friend to Client):\nHey! Congrats on the {'new house' if house_price > 0 else 'promotion'}! How's everything going?")
    else:
        emails.append("Email 2 (Client to Self):\nShould I really be spending money on insurance? I'm single, no dependents...")
    
    if house_price > 0:
        emails.append(f"Email 3 (Client to Friend):\nThanks! {'House cost' if has_spouse else 'Got a place for'} ${house_price:,}. Mortgage is ${monthly_mortgage:,}/mo. {'Bit nervous about it TBH' if skepticism > 6 else 'Excited but need to plan better'}.")
    else:
        emails.append(f"Email 3 (Client to Friend):\nStill renting. Trying to save up but also thinking about insurance and retirement.")
    
    emails.append(f"Email 4 (Client to HR):\nCan you send me info on the company life insurance? I think I have 2x salary?")
    
    emails.append(f"Email 5 (HR to Client):\nYes, you have ${work_life_insurance:,} coverage (2x your ${salary:,} salary). You can purchase additional coverage during open enrollment.")
    
    # Email 6-15: Research and concerns
    if has_spouse:
        emails.append(f"Email 6 (Client to Spouse):\nSo I've been thinking... if something happened to me, you'd get ${work_life_insurance:,} from work. Is that enough?")
        emails.append(f"Email 7 (Spouse to Client):\nI don't know... with the {'mortgage, car loans, and daycare' if num_children > 0 else 'mortgage and bills'}? I'd be terrified. Can we talk to someone?")
    else:
        emails.append(f"Email 6 (Client to Self):\nMaybe I should get some coverage anyway. What if I get married or have kids later?")
        emails.append(f"Email 7 (Client to Friend):\nThinking about getting life insurance even though I'm single. Good idea or waste of money?")
    
    emails.append(f"Email 8 (Client to Insurance Advisor):\nHi, I was referred by my colleague Tom. I'd like to discuss life insurance options.")
    
    emails.append(f"Email 9 (Advisor to Client):\nGreat to hear from you! Let's schedule a call. Can you share some basic info about your situation?")
    
    family_info = f"married, {num_children} kid{'s' if num_children != 1 else ''}" if has_spouse else "single, no kids"
    debt_info = f"${student_loans:,} in student loans, ${car_loan:,} car loan" if student_loans + car_loan > 0 else "minimal debt"
    
    emails.append(f"Email 10 (Client to Advisor):\nSure. I'm {age}, {family_info}. Salary ${salary:,}{f', spouse makes ${spouse_salary:,}' if has_spouse else ''}. {'Just bought a house (${:,} mortgage)'.format(house_price) if house_price > 0 else 'Renting currently'}. Have about ${savings_401k:,} in 401k, ${emergency_fund:,} emergency fund. {debt_info}.")
    
    emails.append(f"Email 11 (Client to Self):\nBefore I meet with this advisor, let me see what the internet says...")
    
    emails.append(f"Email 12 (Client to Friend):\nDo you have life insurance? This advisor wants to meet but I don't want to get sold something I don't need.")
    
    emails.append(f"Email 13 (Friend to Client):\nI just have term life through work. My buddy said whole life is a scam - just get cheap term and invest the difference.")
    
    emails.append(f"Email 14 (Client to Self):\nHmm, need to research this more. What's the difference between term and whole life?")
    
    if has_spouse:
        emails.append(f"Email 15 (Client to Spouse):\nI'm meeting with the insurance guy next week. He's going to try to sell us something expensive, I can already tell.")
    else:
        emails.append(f"Email 15 (Client to Self):\nMeeting scheduled. Need to be careful not to overspend on this.")
    
    # Email 16-30: Pre-meeting skepticism
    if has_spouse:
        emails.append(f"Email 16 (Spouse to Client):\nJust listen to what he says. We need SOMETHING. I can't sleep thinking about what would happen.")
    else:
        emails.append(f"Email 16 (Client to Friend):\nWhat if I just invest that money instead? Seems smarter.")
    
    coverage_amount = random.choice([500000, 750000, 1000000])
    emails.append(f"Email 17 (Client to Advisor):\nI've been doing some research. I think I just need term life insurance, maybe ${coverage_amount:,} for 20 years?")
    
    emails.append(f"Email 18 (Advisor to Client):\nThat's a great starting point! Term is definitely part of the solution. Let's discuss a comprehensive approach that also includes permanent coverage and disability protection.")
    
    emails.append(f"Email 19 (Client to Self):\n\"Comprehensive approach\" = expensive. I knew it.")
    
    emails.append(f"Email 20 (Client to Friend):\nThe insurance guy is already pushing whole life and disability insurance. I just want simple term coverage!")
    
    emails.append(f"Email 21 (Friend to Client):\nYeah, they make commission on that stuff. Just get term from SelectQuote or Policygenius online.")
    
    if has_spouse:
        emails.append(f"Email 22 (Client to Spouse):\nMaybe we should just get term insurance online? It's way cheaper.")
        emails.append(f"Email 23 (Spouse to Client):\nI don't know... what if we're missing something? Let's at least hear him out.")
    else:
        emails.append(f"Email 22 (Client to Self):\nOnline term insurance is like $40/month. Advisor will probably quote $300+.")
        emails.append(f"Email 23 (Client to Friend):\nGoing to the meeting but staying skeptical.")
    
    emails.append(f"Email 24 (Client to Advisor):\nOK, I'm open to learning more. But I'm pretty skeptical about whole life insurance.")
    
    emails.append(f"Email 25 (Advisor to Client):\nI appreciate your honesty! Skepticism is healthy. Let me show you how the pieces fit together for your specific situation.")
    
    emails.append(f"Email 26 (Client to Self):\nMeeting is tomorrow. Need to prepare questions. Don't want to be pressured into anything.")
    
    questions = "Why whole life? What are the fees? Can we just get term? What about disability insurance - do we really need it?"
    emails.append(f"Email 27 (Client to {'Spouse' if has_spouse else 'Self'}):\nQuestions for tomorrow: {questions}")
    
    if has_spouse:
        emails.append(f"Email 28 (Spouse to Client):\nGood questions. Also ask: what happens if you change jobs? Can we afford this?")
    else:
        emails.append(f"Email 28 (Client to Self):\nAlso need to ask about flexibility if my situation changes.")
    
    emails.append(f"Email 29 (Client to Advisor - After Meeting):\nThanks for the presentation. It's a lot to think about. Can you send me the proposal in writing?")
    
    monthly_premium = random.randint(600, 1200)
    emails.append(f"Email 30 (Advisor to Client):\nAbsolutely! I'll send over a detailed proposal. To recap: ${coverage_amount:,} 20-year term, ${int(coverage_amount/2):,} whole life, disability coverage at ${int(salary*0.6/12):,}/mo benefit, and we discussed the cash buffer strategy.")
    
    # Email 31-45: Post-meeting analysis
    if has_spouse:
        emails.append(f"Email 31 (Client to Spouse):\nHe's recommending like ${monthly_premium:,}/month in premiums. That's a lot.")
        emails.append(f"Email 32 (Spouse to Client):\nWhat does that include?")
        emails.append(f"Email 33 (Client to Spouse):\nTerm life, whole life, disability insurance, and some investment thing. The whole life is like ${int(monthly_premium*0.5):,}/mo alone.")
        emails.append(f"Email 34 (Spouse to Client):\nCan we afford that? That's almost ${monthly_premium*12:,} a year.")
    else:
        emails.append(f"Email 31 (Client to Self):\n${monthly_premium:,}/month seems excessive for someone single.")
        emails.append(f"Email 32 (Client to Friend):\nQuote came in at ${monthly_premium:,}/month. Thoughts?")
        emails.append(f"Email 33 (Friend to Client):\nDude, that's insane. I pay $50/month for term life.")
        emails.append(f"Email 34 (Client to Self):\nFriend says it's too much, but he also doesn't have my income or assets.")
    
    
    # Pre-compute values to avoid nested f-string issues
    advisor_gender = 'he' if random.random() > 0.5 else 'she'
    emails.append(f"Email 35 (Client to Self):\\nNeed to run this by ChatGPT or something. See if this is reasonable or if {advisor_gender}'s ripping me off.")
    
    emails.append(f"Email 36 (Client to Friend):\\nGot the proposal. ${monthly_premium:,}/month. Does that sound crazy to you?")
    
    # Email 37 - pre-compute all conditional values
    friend_greeting = 'Dude' if random.random() > 0.5 else 'Yeah'
    amount_desc = 'insane' if skepticism > 7 else 'a lot'
    friend_advice = "I pay $50/month for term life. You're getting screwed." if skepticism > 7 else "Make sure you understand what you're getting."
    emails.append(f"Email 37 (Friend to Client):\\n{friend_greeting}, that's {amount_desc}. {friend_advice}")
    
    # Email 38
    friend_gender2 = 'he' if random.random() > 0.5 else 'she'
    comparison = 'family or a mortgage' if has_spouse else 'high income'
    emails.append(f"Email 38 (Client to Self):\\nOK, friend says it's too much, but {friend_gender2} also doesn't have a {comparison} like I do. Need objective analysis.")

    
    if has_spouse:
        emails.append(f"Email 39 (Client to Spouse):\nI'm going to get a second opinion on this proposal before we decide.")
        emails.append(f"Email 40 (Spouse to Client):\nFrom who?")
        emails.append(f"Email 41 (Client to Spouse):\nI'll ask AI to review it. ChatGPT is pretty good at this stuff.")
    else:
        emails.append(f"Email 39 (Client to Self):\nLet me ask AI for an objective review.")
        emails.append(f"Email 40 (Client to Friend):\nGoing to run this by ChatGPT before deciding.")
        emails.append(f"Email 41 (Friend to Client):\nSmart. AI won't try to sell you anything.")
    
    emails.append(f"Email 42 (Client to Self):\nLet me also check Reddit. What do people say about insurance advisors?")
    
    reddit_sentiment = "overpriced and commission-driven" if skepticism > 6 else "mixed reviews - some good, some bad"
    reddit_reaction = 'Oh no.' if skepticism > 6 else 'Interesting.'; reddit_conclusion = "Now I'm really skeptical." if skepticism > 6 else "Need to be careful."; emails.append(f"Email 43 (Client to Self - After Reddit):\\n{reddit_reaction} Reddit says advisors are {reddit_sentiment}. {reddit_conclusion}")
    
    if has_spouse:
        emails.append(f"Email 44 (Client to Spouse):\nReddit is saying insurance advisors are {reddit_sentiment}. Maybe we should just get term insurance online.")
        college_or_future = "kids' college fund" if num_children > 0 else "future"; emails.append(f"Email 45 (Spouse to Client):\\nBut what about the disability insurance? And the whole life thing for the {college_or_future}?")
    else:
        emails.append(f"Email 44 (Client to Self):\nReddit confirms my suspicions. Online term insurance might be the way to go.")
        emails.append(f"Email 45 (Client to Friend):\nThinking of just getting term online and skipping the advisor.")
    
    # Email 46-50: Final deliberation
    email46_reaction = "I don't know." if skepticism > 6 else "This is confusing."; emails.append(f"Email 46 (Client to {'Spouse' if has_spouse else 'Self'}):\\n{email46_reaction} The advisor made it sound good, but the internet says it's a bad deal.")
    
    emails.append(f"Email 47 (Client to Self):\nThis is so confusing. Who do I trust? The professional advisor or the internet?")
    
    emails.append(f"Email 48 (Client to Advisor):\nHi, I have some questions about the proposal. Can we schedule another call?")
    
    emails.append(f"Email 49 (Advisor to Client):\nOf course! I'm here to answer any questions. When works for you?")
    
    emails.append(f"Email 50 (Client to Self):\nBefore that call, I need to really understand what AI thinks about this proposal. Let me upload it and see what it says.")
    
    return "\n\n".join(emails)


# Test function
if __name__ == "__main__":
    profile = generate_random_client_profile()
    print(profile)
    print(f"\n\nLength: {len(profile)} characters")




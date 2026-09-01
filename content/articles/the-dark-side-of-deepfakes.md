---
title: The Dark Side of Deepfakes
category: Technology
author: Shadrach
author_bio: Shadrach is the founder and editor of BlogSphere, a cybersecurity graduate and web developer with a passion for making complex topics clear and accessible. Based in Nigeria.
date: 2026-08-14
read_time: 7
tags: technology, ai, deepfakes
featured_image: /static/uploads/15cc823e5bfc41f3803b414e23aca8ec.webp
featured_image_width: 1800
featured_image_height: 1200
---

# The Dark Side of Deepfakes

## Understanding Deepfakes: A Double-Edged Sword  
Deepfakes are synthetic media, image, audio, or video, produced with AI to realistically manipulate or invent a person's likeness or voice. The term blends "deep learning" and "fake," and the technology genuinely cuts both ways: it's already used legitimately for film de-aging and digital doubles, with real potential in education and accessibility. But that same capability has become a proven tool for fraud, harassment, and disinformation, and one that's advanced far faster than institutions have managed to keep up with.

## The Technology Behind the Illusion  
![Visualization of a generative adversarial network creating synthetic media](/static/uploads/the-dark-side-of-deepfakes-img1.jpg)
Deepfakes are typically created using a generative adversarial network (GAN), two neural networks trained against each other, one generating fake content and the other trying to detect it, producing increasingly convincing results over successive rounds. What's really changed isn't so much the underlying technology as its accessibility: McAfee research shows as little as three seconds of audio is now enough to generate a usable voice clone, meaning a single public talk, podcast appearance, or earnings call recording gives an attacker sufficient raw material. What once required a research lab can now be done on consumer hardware.

## Real-World Fraud: What's Actually Happened

This isn't hypothetical. In January 2024, a finance employee at the Hong Kong office of Arup, the UK-headquartered engineering firm, joined a video call with people who appeared to be the company's CFO and other senior colleagues, all of whom turned out to be deepfakes. The employee went on to authorize 15 transfers totaling roughly $25.6 million before the fraud was discovered. In May 2024, scammers attempted a similar scheme against WPP, using a cloned voice and YouTube footage of CEO Mark Read in a fake Microsoft Teams meeting to try to pressure an agency leader into setting up a new business and handing over money and personal details; the attempt failed thanks to the target's vigilance, though no single verification question is what stopped it. In July 2024, Ferrari narrowly avoided a comparable scam when an executive, growing suspicious of WhatsApp messages and a cloned-voice call impersonating CEO Benedetto Vigna, asked the caller to name a book Vigna had recently recommended to him, a question the impersonator couldn't answer, ending the call before any transfer took place.
 
The FBI's Internet Crime Report for 2025 offers the most rigorously sourced figure here, and it's worth noting the cases above span multiple countries, reinforcing that this is a global pattern rather than an isolated one. The FBI's report counted 22,364 complaints referencing AI, with total reported U.S. losses of roughly $893 million in a single year. It's worth treating more dramatic numbers circulating in "deepfake statistics" roundups with real skepticism, many originate from vendors selling detection software, and get repeated and inflated across websites without independent verification. The FBI figure, drawn from an actual audited complaint process, is the more defensible baseline, and even the FBI's own reporting suggests it's likely an undercount, since AI involvement is only counted when victims recognize and report it themselves.

## Ethical Dilemmas and Societal Impact
Non-consensual explicit deepfake content, which overwhelmingly targets women, both private individuals and public figures, is the most direct harm here. It's a clear, serious wrong independent of any financial angle: a breach of consent and likeness with lasting psychological consequences, not just a monetary one.
 
The broader societal risk is that as forgeries get more numerous and more convincing, genuine evidence becomes easier to dismiss as fake. According to iProov research, only about 0.1% of people could reliably distinguish real content from deepfakes in controlled testing, while roughly 60% believed they were capable of telling the difference. That gap between confidence and actual ability is arguably the more corrosive long-term problem, since it undermines the basic trust visual and audio evidence has always carried, one convincing fake at a time.

## Deepfakes in Cybersecurity and Misinformation  
![Illustration of a cybersecurity threat involving voice or video impersonation](/static/uploads/the-dark-side-of-deepfakes-img2.jpg)
Executive impersonation fraud, using a CEO or CFO's cloned voice or likeness to authorize a transaction, is a distinct, fast-growing category the FBI now tracks separately, driven largely by how convincing and low-effort it's become to fake a call or video appearance. Security researchers at Pindrop reported a 680% year-over-year increase in voice-cloning fraud, and separate survey data found 67.5% of U.S. consumers report specific concern about deepfake and voice-clone attacks in banking contexts.

## Legal Challenges and Regulatory Efforts  
The regulatory landscape has moved faster than most coverage anticipated even a year or two ago. In the U.S., the federal TAKE IT DOWN Act, the first federal law criminalizing nonconsensual intimate AI-generated imagery, was signed in May 2025, with platforms given until May 2026 to establish notice-and-removal systems for flagged content. At the state level, most U.S. states have passed some form of deepfake-related law since 2022. In the EU, the AI Act's transparency requirements, mandating disclosure when content is AI-generated, take effect August 2, 2026, with penalties of up to €35 million or 7% of global annual turnover for non-compliance.
 
Coverage still has real gaps, though: there's currently no federal U.S. statute specifically prohibiting deepfake use in financial fraud, leaving prosecutors to rely on existing wire fraud, fraud, and impersonation laws that weren't written with this technology in mind. Cross-border enforcement remains the hardest problem, since attackers operating outside a victim's jurisdiction are difficult to prosecute even where strong domestic law exists.

## Fighting Back: Tools and Strategies for Detection  
![Person verifying identity through a secure video call process](/static/uploads/the-dark-side-of-deepfakes-img3.jpg)

AI-powered detection tools show accuracy in the 45 to 50% range in real-world conditions, adversarially optimized fake videos, compressed footage, varied lighting, a significant drop from lab performance. With human detection accuracy close to
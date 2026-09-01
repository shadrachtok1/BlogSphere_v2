#!/usr/bin/env python3
"""
One-time script to download hotlinked Pexels/Unsplash images
and save them into static/uploads/ with the filenames the
articles now reference.

Usage:
  pip install requests
  python download_images.py
"""

import os
import requests

OUTPUT_DIR = "static/uploads"

IMAGES = [
    ('https://images.pexels.com/photos/17888109/pexels-photo-17888109.jpeg', 'ai-in-everyday-life-img1.jpg'),
    ('https://images.unsplash.com/photo-1608377205619-03a0b4c4e270?q=80&w=710&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'ai-in-everyday-life-img2.jpg'),
    ('https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'ai-in-everyday-life-img3.jpg'),
    ('https://images.unsplash.com/photo-1603638725135-928baf863eff?q=80&w=735&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'ai-in-everyday-life-img4.jpg'),
    ('https://images.unsplash.com/photo-1651054558996-03455fe2702f?q=80&w=880&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'blockchain-technology-img1.jpg'),
    ('https://images.unsplash.com/photo-1631864032976-cef7f00fea43?q=80&w=1331&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'blockchain-technology-img2.jpg'),
    ('https://images.pexels.com/photos/9162030/pexels-photo-9162030.jpeg', 'butterflies-in-your-stomach-are-real-img1.jpg'),
    ('https://images.pexels.com/photos/8297132/pexels-photo-8297132.jpeg', 'butterflies-in-your-stomach-are-real-img2.jpg'),
    ('https://images.pexels.com/photos/3760044/pexels-photo-3760044.jpeg', 'butterflies-in-your-stomach-are-real-img3.jpg'),
    ('https://images.pexels.com/photos/4498193/pexels-photo-4498193.jpeg', 'can-5-minute-workout-really-transform-your-health-img1.jpg'),
    ('https://images.pexels.com/photos/12932673/pexels-photo-12932673.jpeg', 'can-5-minute-workout-really-transform-your-health-img2.jpg'),
    ('https://images.pexels.com/photos/2294361/pexels-photo-2294361.jpeg', 'can-5-minute-workout-really-transform-your-health-img3.jpg'),
    ('https://images.pexels.com/photos/8036745/pexels-photo-8036745.jpeg', 'dark-mode-vs-light-mode-which-one-actually-helps-your-eyes-and-focus-img1.jpg'),
    ('https://images.unsplash.com/photo-1607027340850-44448bd87dcb?q=80&w=1073&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'dark-mode-vs-light-mode-which-one-actually-helps-your-eyes-and-focus-img2.jpg'),
    ('https://images.unsplash.com/photo-1623658962582-a09214e103e6?q=80&w=735&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'dark-mode-vs-light-mode-which-one-actually-helps-your-eyes-and-focus-img3.jpg'),
    ('https://images.unsplash.com/photo-1758687127246-762d3892326c?q=80&w=1332&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'future-of-remote-work-img1.jpg'),
    ('https://images.pexels.com/photos/30535638/pexels-photo-30535638.jpeg', 'future-of-remote-work-img2.jpg'),
    ('https://images.unsplash.com/photo-1760346546839-aced24accdff?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'future-of-remote-work-img3.jpg'),
    ('https://images.pexels.com/photos/7644158/pexels-photo-7644158.jpeg', 'future-of-remote-work-img4.jpg'),
    ('https://images.pexels.com/photos/7276172/pexels-photo-7276172.jpeg', 'how-to-turn-a-passion-into-profit-without-burning-out-img1.jpg'),
    ('https://images.pexels.com/photos/6956344/pexels-photo-6956344.jpeg/', 'how-to-turn-a-passion-into-profit-without-burning-out-img2.jpg'),
    ('https://images.pexels.com/photos/38337697/pexels-photo-38337697.jpeg', 'how-to-turn-a-passion-into-profit-without-burning-out-img3.jpg'),
    ('https://images.pexels.com/photos/6837792/pexels-photo-6837792.jpeg', 'how-to-turn-a-passion-into-profit-without-burning-out-img4.jpg'),
    ('https://images.pexels.com/photos/6250995/pexels-photo-6250995.jpeg', 'how-to-turn-a-passion-into-profit-without-burning-out-img5.jpg'),
    ('https://images.pexels.com/photos/37494738/pexels-photo-37494738.jpeg', 'productivity-hacks-img1.jpg'),
    ('https://images.pexels.com/photos/2565919/pexels-photo-2565919.jpeg', 'productivity-hacks-img2.jpg'),
    ('https://images.pexels.com/photos/8938641/pexels-photo-8938641.jpeg', 'productivity-hacks-img3.jpg'),
    ('https://images.unsplash.com/photo-1604480131833-5d7aea770e1c?q=80&w=1332&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'productivity-hacks-img4.jpg'),
    ('https://images.unsplash.com/photo-1607523751915-5291fab91551?q=80&w=1074&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'productivity-hacks-img5.jpg'),
    ('https://images.pexels.com/photos/9017612/pexels-photo-9017612.jpeg', 'productivity-hacks-img6.jpg'),
    ('https://images.pexels.com/photos/5417845/pexels-photo-5417845.jpeg', 'sleep-optimization-science-backed-hacks-for-perfect-rest-img1.jpg'),
    ('https://images.pexels.com/photos/6940373/pexels-photo-6940373.jpeg', 'sleep-optimization-science-backed-hacks-for-perfect-rest-img2.jpg'),
    ('https://images.pexels.com/photos/27164976/pexels-photo-27164976.jpeg', 'sleep-optimization-science-backed-hacks-for-perfect-rest-img3.jpg'),
    ('https://images.pexels.com/photos/7575745/pexels-photo-7575745.jpeg', 'sleep-optimization-science-backed-hacks-for-perfect-rest-img4.jpg'),
    ('https://images.pexels.com/photos/6541417/pexels-photo-6541417.jpeg', 'sleep-optimization-science-backed-hacks-for-perfect-rest-img5.jpg'),
    ('https://images.pexels.com/photos/33723582/pexels-photo-33723582.jpeg', 'sleep-optimization-science-backed-hacks-for-perfect-rest-img6.jpg'),
    ('https://images.pexels.com/photos/11743785/pexels-photo-11743785.jpeg', 'subscription-creep-how-small-recurring-charges-quietly-drain-a-budget-img1.jpg'),
    ('https://images.pexels.com/photos/7054413/pexels-photo-7054413.jpeg', 'subscription-creep-how-small-recurring-charges-quietly-drain-a-budget-img2.jpg'),
    ('https://images.pexels.com/photos/6202994/pexels-photo-6202994.jpeg', 'the-5-second-rule-for-decision-making-img1.jpg'),
    ('https://images.pexels.com/photos/35678475/pexels-photo-35678475.jpeg', 'the-5-second-rule-for-decision-making-img2.jpg'),
    ('https://images.pexels.com/photos/1127120/pexels-photo-1127120.jpeg', 'the-5-second-rule-for-decision-making-img3.jpg'),
    ('https://images.pexels.com/photos/9016985/pexels-photo-9016985.jpeg', 'the-5-second-rule-for-decision-making-img4.jpg'),
    ('https://images.unsplash.com/photo-1639756012443-b06372f0b6ef?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'the-difference-between-being-tired-and-being-burned-out-img1.jpg'),
    ('https://images.unsplash.com/photo-1618517047922-d18a5a36c109?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'the-difference-between-being-tired-and-being-burned-out-img2.jpg'),
    ('https://images.unsplash.com/photo-1683362673136-0c078ea99d47?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'the-difference-between-being-tired-and-being-burned-out-img3.jpg'),
    ('https://images.pexels.com/photos/8939959/pexels-photo-8939959.jpeg', 'the-difference-between-being-tired-and-being-burned-out-img4.jpg'),
    ('https://images.pexels.com/photos/8560680/pexels-photo-8560680.jpeg', 'the-difference-between-being-tired-and-being-burned-out-img5.jpg'),
    ('https://images.pexels.com/photos/14299950/pexels-photo-14299950.jpeg', 'the-psychology-of-color-how-to-boost-user-engagement-through-design-img1.jpg'),
    ('https://images.pexels.com/photos/5582594/pexels-photo-5582594.jpeg', 'the-psychology-of-color-how-to-boost-user-engagement-through-design-img2.jpg'),
    ('https://images.pexels.com/photos/6214143/pexels-photo-6214143.jpeg', 'the-psychology-of-spending-img1.jpg'),
    ('https://images.pexels.com/photos/7821899/pexels-photo-7821899.jpeg', 'the-psychology-of-spending-img2.jpg'),
    ('https://images.pexels.com/photos/36730404/pexels-photo-36730404.jpeg', 'the-psychology-of-spending-img3.jpg'),
    ('https://images.pexels.com/photos/6694952/pexels-photo-6694952.jpeg', 'the-psychology-of-spending-img4.jpg'),
    ('https://images.pexels.com/photos/2398354/pexels-photo-2398354.jpeg', 'too-much-to-watch-the-paralysis-of-infinite-streaming-choice-img1.jpg'),
    ('https://images.pexels.com/photos/35490296/pexels-photo-35490296.jpeg', 'too-much-to-watch-the-paralysis-of-infinite-streaming-choice-img2.jpg'),
    ('https://images.pexels.com/photos/6958469/pexels-photo-6958469.jpeg', 'too-much-to-watch-the-paralysis-of-infinite-streaming-choice-img3.jpg'),
    ('https://images.pexels.com/photos/5081423/pexels-photo-5081423.jpeg', 'too-much-to-watch-the-paralysis-of-infinite-streaming-choice-img4.jpg'),
    ('https://images.pexels.com/photos/7155738/pexels-photo-7155738.jpeg', 'too-much-to-watch-the-paralysis-of-infinite-streaming-choice-img5.jpg'),
    ('https://images.pexels.com/photos/6846257/pexels-photo-6846257.jpeg', 'wearable-tech-trends-that-will-redefine-health-monitoring-img1.jpg'),
    ('https://images.pexels.com/photos/32977239/pexels-photo-32977239.jpeg', 'wearable-tech-trends-that-will-redefine-health-monitoring-img2.jpg'),
    ('https://images.pexels.com/photos/6823514/pexels-photo-6823514.jpeg', 'wearable-tech-trends-that-will-redefine-health-monitoring-img3.jpg'),
    ('https://images.unsplash.com/photo-1610548822783-33fb5cb0e3a8?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjB8fGRvZXMlMjBkZWxldGluZyUyMGFuJTIwYXBwJTIwZXJhc2UlMjBhbGwlMjB5b3VyJTIwZGF0YSUzRnxlbnwwfHwwfHx8Mg%3D%3D', 'what-happens-to-your-data-after-you-delete-an-app-img1.jpg'),
    ('https://images.unsplash.com/photo-1667984390553-7f439e6ae401?q=80&w=1332&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', 'what-happens-to-your-data-after-you-delete-an-app-img2.jpg'),
    ('https://images.pexels.com/photos/8962344/pexels-photo-8962344.jpeg', 'why-renting-might-be-the-smarter-financial-move-in-2026-img1.jpg'),
    ('https://images.pexels.com/photos/7578859/pexels-photo-7578859.jpeg', 'why-renting-might-be-the-smarter-financial-move-in-2026-img2.jpg'),
    ('https://images.pexels.com/photos/7947740/pexels-photo-7947740.jpeg', 'why-renting-might-be-the-smarter-financial-move-in-2026-img3.jpg'),
    ('https://images.pexels.com/photos/12244846/pexels-photo-12244846.jpeg', 'why-renting-might-be-the-smarter-financial-move-in-2026-img4.jpg'),
]

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for url, filename in IMAGES:
        dest = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(dest):
            print(f"skip (exists): {filename}")
            continue
        try:
            r = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
            r.raise_for_status()
            with open(dest, 'wb') as out:
                out.write(r.content)
            print(f"downloaded: {filename}")
        except Exception as e:
            print(f"FAILED: {filename} ({url}) -> {e}")

if __name__ == "__main__":
    main()

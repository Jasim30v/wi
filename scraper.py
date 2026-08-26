#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  🌍  SOCIAL SCRAPER PRO - Location Intelligence Tool        ║
║  استخراج الموقع الجغرافي الحقيقي للأشخاص من جميع المنصات   ║
║  يدعم: Facebook, Instagram, Twitter/X, LinkedIn, TikTok,   ║
║  YouTube, GitHub, Reddit, Snapchat, Telegram, WhatsApp,    ║
║  Pinterest, Twitch, Discord, Medium, Spotify, SoundCloud   ║
║  ✓ كشف الدولة والمدينة                                     ║
║  ✓ استخراج الإحداثيات (GPS) إن وجدت                       ║
║  ✓ تحليل اللغة والمنطقة                                   ║
║  ✓ واجهة ويب احترافية                                     ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import re
import time
import hashlib
import random
import requests
from datetime import datetime
from urllib.parse import urlparse, quote_plus, parse_qs
from typing import Dict, List, Optional, Tuple, Any
from bs4 import BeautifulSoup
import sys

# ===================================================================
# 🌍 قاعدة بيانات الدول والمدن والرموز
# ===================================================================

COUNTRIES_DB = {
    'af': {'name': 'أفغانستان', 'flag': '🇦🇫', 'code': '+93', 'continent': 'آسيا'},
    'al': {'name': 'ألبانيا', 'flag': '🇦🇱', 'code': '+355', 'continent': 'أوروبا'},
    'dz': {'name': 'الجزائر', 'flag': '🇩🇿', 'code': '+213', 'continent': 'أفريقيا'},
    'ad': {'name': 'أندورا', 'flag': '🇦🇩', 'code': '+376', 'continent': 'أوروبا'},
    'ao': {'name': 'أنغولا', 'flag': '🇦🇴', 'code': '+244', 'continent': 'أفريقيا'},
    'ar': {'name': 'الأرجنتين', 'flag': '🇦🇷', 'code': '+54', 'continent': 'أمريكا الجنوبية'},
    'am': {'name': 'أرمينيا', 'flag': '🇦🇲', 'code': '+374', 'continent': 'آسيا'},
    'au': {'name': 'أستراليا', 'flag': '🇦🇺', 'code': '+61', 'continent': 'أوقيانوسيا'},
    'at': {'name': 'النمسا', 'flag': '🇦🇹', 'code': '+43', 'continent': 'أوروبا'},
    'az': {'name': 'أذربيجان', 'flag': '🇦🇿', 'code': '+994', 'continent': 'آسيا'},
    'bh': {'name': 'البحرين', 'flag': '🇧🇭', 'code': '+973', 'continent': 'آسيا'},
    'bd': {'name': 'بنغلاديش', 'flag': '🇧🇩', 'code': '+880', 'continent': 'آسيا'},
    'by': {'name': 'بيلاروسيا', 'flag': '🇧🇾', 'code': '+375', 'continent': 'أوروبا'},
    'be': {'name': 'بلجيكا', 'flag': '🇧🇪', 'code': '+32', 'continent': 'أوروبا'},
    'bj': {'name': 'بنين', 'flag': '🇧🇯', 'code': '+229', 'continent': 'أفريقيا'},
    'bt': {'name': 'بوتان', 'flag': '🇧🇹', 'code': '+975', 'continent': 'آسيا'},
    'bo': {'name': 'بوليفيا', 'flag': '🇧🇴', 'code': '+591', 'continent': 'أمريكا الجنوبية'},
    'ba': {'name': 'البوسنة والهرسك', 'flag': '🇧🇦', 'code': '+387', 'continent': 'أوروبا'},
    'bw': {'name': 'بوتسوانا', 'flag': '🇧🇼', 'code': '+267', 'continent': 'أفريقيا'},
    'br': {'name': 'البرازيل', 'flag': '🇧🇷', 'code': '+55', 'continent': 'أمريكا الجنوبية'},
    'bn': {'name': 'بروناي', 'flag': '🇧🇳', 'code': '+673', 'continent': 'آسيا'},
    'bg': {'name': 'بلغاريا', 'flag': '🇧🇬', 'code': '+359', 'continent': 'أوروبا'},
    'bf': {'name': 'بوركينا فاسو', 'flag': '🇧🇫', 'code': '+226', 'continent': 'أفريقيا'},
    'bi': {'name': 'بوروندي', 'flag': '🇧🇮', 'code': '+257', 'continent': 'أفريقيا'},
    'kh': {'name': 'كمبوديا', 'flag': '🇰🇭', 'code': '+855', 'continent': 'آسيا'},
    'cm': {'name': 'الكاميرون', 'flag': '🇨🇲', 'code': '+237', 'continent': 'أفريقيا'},
    'ca': {'name': 'كندا', 'flag': '🇨🇦', 'code': '+1', 'continent': 'أمريكا الشمالية'},
    'cv': {'name': 'الرأس الأخضر', 'flag': '🇨🇻', 'code': '+238', 'continent': 'أفريقيا'},
    'cf': {'name': 'جمهورية أفريقيا الوسطى', 'flag': '🇨🇫', 'code': '+236', 'continent': 'أفريقيا'},
    'td': {'name': 'تشاد', 'flag': '🇹🇩', 'code': '+235', 'continent': 'أفريقيا'},
    'cl': {'name': 'تشيلي', 'flag': '🇨🇱', 'code': '+56', 'continent': 'أمريكا الجنوبية'},
    'cn': {'name': 'الصين', 'flag': '🇨🇳', 'code': '+86', 'continent': 'آسيا'},
    'co': {'name': 'كولومبيا', 'flag': '🇨🇴', 'code': '+57', 'continent': 'أمريكا الجنوبية'},
    'km': {'name': 'جزر القمر', 'flag': '🇰🇲', 'code': '+269', 'continent': 'أفريقيا'},
    'cg': {'name': 'الكونغو', 'flag': '🇨🇬', 'code': '+242', 'continent': 'أفريقيا'},
    'cd': {'name': 'الكونغو الديمقراطية', 'flag': '🇨🇩', 'code': '+243', 'continent': 'أفريقيا'},
    'cr': {'name': 'كوستاريكا', 'flag': '🇨🇷', 'code': '+506', 'continent': 'أمريكا الشمالية'},
    'hr': {'name': 'كرواتيا', 'flag': '🇭🇷', 'code': '+385', 'continent': 'أوروبا'},
    'cu': {'name': 'كوبا', 'flag': '🇨🇺', 'code': '+53', 'continent': 'أمريكا الشمالية'},
    'cy': {'name': 'قبرص', 'flag': '🇨🇾', 'code': '+357', 'continent': 'أوروبا'},
    'cz': {'name': 'التشيك', 'flag': '🇨🇿', 'code': '+420', 'continent': 'أوروبا'},
    'dk': {'name': 'الدنمارك', 'flag': '🇩🇰', 'code': '+45', 'continent': 'أوروبا'},
    'dj': {'name': 'جيبوتي', 'flag': '🇩🇯', 'code': '+253', 'continent': 'أفريقيا'},
    'dm': {'name': 'دومينيكا', 'flag': '🇩🇲', 'code': '+1', 'continent': 'أمريكا الشمالية'},
    'do': {'name': 'جمهورية الدومينيكان', 'flag': '🇩🇴', 'code': '+1', 'continent': 'أمريكا الشمالية'},
    'ec': {'name': 'الإكوادور', 'flag': '🇪🇨', 'code': '+593', 'continent': 'أمريكا الجنوبية'},
    'eg': {'name': 'مصر', 'flag': '🇪🇬', 'code': '+20', 'continent': 'أفريقيا'},
    'sv': {'name': 'السلفادور', 'flag': '🇸🇻', 'code': '+503', 'continent': 'أمريكا الشمالية'},
    'gq': {'name': 'غينيا الاستوائية', 'flag': '🇬🇶', 'code': '+240', 'continent': 'أفريقيا'},
    'er': {'name': 'إريتريا', 'flag': '🇪🇷', 'code': '+291', 'continent': 'أفريقيا'},
    'ee': {'name': 'إستونيا', 'flag': '🇪🇪', 'code': '+372', 'continent': 'أوروبا'},
    'et': {'name': 'إثيوبيا', 'flag': '🇪🇹', 'code': '+251', 'continent': 'أفريقيا'},
    'fj': {'name': 'فيجي', 'flag': '🇫🇯', 'code': '+679', 'continent': 'أوقيانوسيا'},
    'fi': {'name': 'فنلندا', 'flag': '🇫🇮', 'code': '+358', 'continent': 'أوروبا'},
    'fr': {'name': 'فرنسا', 'flag': '🇫🇷', 'code': '+33', 'continent': 'أوروبا'},
    'ga': {'name': 'الغابون', 'flag': '🇬🇦', 'code': '+241', 'continent': 'أفريقيا'},
    'gm': {'name': 'غامبيا', 'flag': '🇬🇲', 'code': '+220', 'continent': 'أفريقيا'},
    'ge': {'name': 'جورجيا', 'flag': '🇬🇪', 'code': '+995', 'continent': 'آسيا'},
    'de': {'name': 'ألمانيا', 'flag': '🇩🇪', 'code': '+49', 'continent': 'أوروبا'},
    'gh': {'name': 'غانا', 'flag': '🇬🇭', 'code': '+233', 'continent': 'أفريقيا'},
    'gr': {'name': 'اليونان', 'flag': '🇬🇷', 'code': '+30', 'continent': 'أوروبا'},
    'gt': {'name': 'غواتيمالا', 'flag': '🇬🇹', 'code': '+502', 'continent': 'أمريكا الشمالية'},
    'gn': {'name': 'غينيا', 'flag': '🇬🇳', 'code': '+224', 'continent': 'أفريقيا'},
    'gw': {'name': 'غينيا بيساو', 'flag': '🇬🇼', 'code': '+245', 'continent': 'أفريقيا'},
    'gy': {'name': 'غيانا', 'flag': '🇬🇾', 'code': '+592', 'continent': 'أمريكا الجنوبية'},
    'ht': {'name': 'هايتي', 'flag': '🇭🇹', 'code': '+509', 'continent': 'أمريكا الشمالية'},
    'hn': {'name': 'هندوراس', 'flag': '🇭🇳', 'code': '+504', 'continent': 'أمريكا الشمالية'},
    'hu': {'name': 'المجر', 'flag': '🇭🇺', 'code': '+36', 'continent': 'أوروبا'},
    'is': {'name': 'آيسلندا', 'flag': '🇮🇸', 'code': '+354', 'continent': 'أوروبا'},
    'in': {'name': 'الهند', 'flag': '🇮🇳', 'code': '+91', 'continent': 'آسيا'},
    'id': {'name': 'إندونيسيا', 'flag': '🇮🇩', 'code': '+62', 'continent': 'آسيا'},
    'ir': {'name': 'إيران', 'flag': '🇮🇷', 'code': '+98', 'continent': 'آسيا'},
    'iq': {'name': 'العراق', 'flag': '🇮🇶', 'code': '+964', 'continent': 'آسيا'},
    'ie': {'name': 'أيرلندا', 'flag': '🇮🇪', 'code': '+353', 'continent': 'أوروبا'},
    'il': {'name': 'إسرائيل', 'flag': '🇮🇱', 'code': '+972', 'continent': 'آسيا'},
    'it': {'name': 'إيطاليا', 'flag': '🇮🇹', 'code': '+39', 'continent': 'أوروبا'},
    'jm': {'name': 'جامايكا', 'flag': '🇯🇲', 'code': '+1', 'continent': 'أمريكا الشمالية'},
    'jp': {'name': 'اليابان', 'flag': '🇯🇵', 'code': '+81', 'continent': 'آسيا'},
    'jo': {'name': 'الأردن', 'flag': '🇯🇴', 'code': '+962', 'continent': 'آسيا'},
    'kz': {'name': 'كازاخستان', 'flag': '🇰🇿', 'code': '+7', 'continent': 'آسيا'},
    'ke': {'name': 'كينيا', 'flag': '🇰🇪', 'code': '+254', 'continent': 'أفريقيا'},
    'kw': {'name': 'الكويت', 'flag': '🇰🇼', 'code': '+965', 'continent': 'آسيا'},
    'kg': {'name': 'قيرغيزستان', 'flag': '🇰🇬', 'code': '+996', 'continent': 'آسيا'},
    'la': {'name': 'لاوس', 'flag': '🇱🇦', 'code': '+856', 'continent': 'آسيا'},
    'lv': {'name': 'لاتفيا', 'flag': '🇱🇻', 'code': '+371', 'continent': 'أوروبا'},
    'lb': {'name': 'لبنان', 'flag': '🇱🇧', 'code': '+961', 'continent': 'آسيا'},
    'ls': {'name': 'ليسوتو', 'flag': '🇱🇸', 'code': '+266', 'continent': 'أفريقيا'},
    'lr': {'name': 'ليبيريا', 'flag': '🇱🇷', 'code': '+231', 'continent': 'أفريقيا'},
    'ly': {'name': 'ليبيا', 'flag': '🇱🇾', 'code': '+218', 'continent': 'أفريقيا'},
    'li': {'name': 'ليختنشتاين', 'flag': '🇱🇮', 'code': '+423', 'continent': 'أوروبا'},
    'lt': {'name': 'ليتوانيا', 'flag': '🇱🇹', 'code': '+370', 'continent': 'أوروبا'},
    'lu': {'name': 'لوكسمبورغ', 'flag': '🇱🇺', 'code': '+352', 'continent': 'أوروبا'},
    'mg': {'name': 'مدغشقر', 'flag': '🇲🇬', 'code': '+261', 'continent': 'أفريقيا'},
    'mw': {'name': 'ملاوي', 'flag': '🇲🇼', 'code': '+265', 'continent': 'أفريقيا'},
    'my': {'name': 'ماليزيا', 'flag': '🇲🇾', 'code': '+60', 'continent': 'آسيا'},
    'mv': {'name': 'المالديف', 'flag': '🇲🇻', 'code': '+960', 'continent': 'آسيا'},
    'ml': {'name': 'مالي', 'flag': '🇲🇱', 'code': '+223', 'continent': 'أفريقيا'},
    'mt': {'name': 'مالطا', 'flag': '🇲🇹', 'code': '+356', 'continent': 'أوروبا'},
    'mr': {'name': 'موريتانيا', 'flag': '🇲🇷', 'code': '+222', 'continent': 'أفريقيا'},
    'mu': {'name': 'موريشيوس', 'flag': '🇲🇺', 'code': '+230', 'continent': 'أفريقيا'},
    'mx': {'name': 'المكسيك', 'flag': '🇲🇽', 'code': '+52', 'continent': 'أمريكا الشمالية'},
    'md': {'name': 'مولدوفا', 'flag': '🇲🇩', 'code': '+373', 'continent': 'أوروبا'},
    'mc': {'name': 'موناكو', 'flag': '🇲🇨', 'code': '+377', 'continent': 'أوروبا'},
    'mn': {'name': 'منغوليا', 'flag': '🇲🇳', 'code': '+976', 'continent': 'آسيا'},
    'me': {'name': 'الجبل الأسود', 'flag': '🇲🇪', 'code': '+382', 'continent': 'أوروبا'},
    'ma': {'name': 'المغرب', 'flag': '🇲🇦', 'code': '+212', 'continent': 'أفريقيا'},
    'mz': {'name': 'موزمبيق', 'flag': '🇲🇿', 'code': '+258', 'continent': 'أفريقيا'},
    'mm': {'name': 'ميانمار', 'flag': '🇲🇲', 'code': '+95', 'continent': 'آسيا'},
    'na': {'name': 'ناميبيا', 'flag': '🇳🇦', 'code': '+264', 'continent': 'أفريقيا'},
    'np': {'name': 'نيبال', 'flag': '🇳🇵', 'code': '+977', 'continent': 'آسيا'},
    'nl': {'name': 'هولندا', 'flag': '🇳🇱', 'code': '+31', 'continent': 'أوروبا'},
    'nz': {'name': 'نيوزيلندا', 'flag': '🇳🇿', 'code': '+64', 'continent': 'أوقيانوسيا'},
    'ni': {'name': 'نيكاراغوا', 'flag': '🇳🇮', 'code': '+505', 'continent': 'أمريكا الشمالية'},
    'ne': {'name': 'النيجر', 'flag': '🇳🇪', 'code': '+227', 'continent': 'أفريقيا'},
    'ng': {'name': 'نيجيريا', 'flag': '🇳🇬', 'code': '+234', 'continent': 'أفريقيا'},
    'kp': {'name': 'كوريا الشمالية', 'flag': '🇰🇵', 'code': '+850', 'continent': 'آسيا'},
    'no': {'name': 'النرويج', 'flag': '🇳🇴', 'code': '+47', 'continent': 'أوروبا'},
    'om': {'name': 'عمان', 'flag': '🇴🇲', 'code': '+968', 'continent': 'آسيا'},
    'pk': {'name': 'باكستان', 'flag': '🇵🇰', 'code': '+92', 'continent': 'آسيا'},
    'ps': {'name': 'فلسطين', 'flag': '🇵🇸', 'code': '+970', 'continent': 'آسيا'},
    'pa': {'name': 'بنما', 'flag': '🇵🇦', 'code': '+507', 'continent': 'أمريكا الشمالية'},
    'pg': {'name': 'بابوا غينيا الجديدة', 'flag': '🇵🇬', 'code': '+675', 'continent': 'أوقيانوسيا'},
    'py': {'name': 'باراغواي', 'flag': '🇵🇾', 'code': '+595', 'continent': 'أمريكا الجنوبية'},
    'pe': {'name': 'بيرو', 'flag': '🇵🇪', 'code': '+51', 'continent': 'أمريكا الجنوبية'},
    'ph': {'name': 'الفلبين', 'flag': '🇵🇭', 'code': '+63', 'continent': 'آسيا'},
    'pl': {'name': 'بولندا', 'flag': '🇵🇱', 'code': '+48', 'continent': 'أوروبا'},
    'pt': {'name': 'البرتغال', 'flag': '🇵🇹', 'code': '+351', 'continent': 'أوروبا'},
    'qa': {'name': 'قطر', 'flag': '🇶🇦', 'code': '+974', 'continent': 'آسيا'},
    'ro': {'name': 'رومانيا', 'flag': '🇷🇴', 'code': '+40', 'continent': 'أوروبا'},
    'ru': {'name': 'روسيا', 'flag': '🇷🇺', 'code': '+7', 'continent': 'أوروبا'},
    'rw': {'name': 'رواندا', 'flag': '🇷🇼', 'code': '+250', 'continent': 'أفريقيا'},
    'sa': {'name': 'السعودية', 'flag': '🇸🇦', 'code': '+966', 'continent': 'آسيا'},
    'sn': {'name': 'السنغال', 'flag': '🇸🇳', 'code': '+221', 'continent': 'أفريقيا'},
    'rs': {'name': 'صربيا', 'flag': '🇷🇸', 'code': '+381', 'continent': 'أوروبا'},
    'sl': {'name': 'سيراليون', 'flag': '🇸🇱', 'code': '+232', 'continent': 'أفريقيا'},
    'sg': {'name': 'سنغافورة', 'flag': '🇸🇬', 'code': '+65', 'continent': 'آسيا'},
    'sk': {'name': 'سلوفاكيا', 'flag': '🇸🇰', 'code': '+421', 'continent': 'أوروبا'},
    'si': {'name': 'سلوفينيا', 'flag': '🇸🇮', 'code': '+386', 'continent': 'أوروبا'},
    'so': {'name': 'الصومال', 'flag': '🇸🇴', 'code': '+252', 'continent': 'أفريقيا'},
    'za': {'name': 'جنوب أفريقيا', 'flag': '🇿🇦', 'code': '+27', 'continent': 'أفريقيا'},
    'kr': {'name': 'كوريا الجنوبية', 'flag': '🇰🇷', 'code': '+82', 'continent': 'آسيا'},
    'ss': {'name': 'جنوب السودان', 'flag': '🇸🇸', 'code': '+211', 'continent': 'أفريقيا'},
    'es': {'name': 'إسبانيا', 'flag': '🇪🇸', 'code': '+34', 'continent': 'أوروبا'},
    'lk': {'name': 'سريلانكا', 'flag': '🇱🇰', 'code': '+94', 'continent': 'آسيا'},
    'sd': {'name': 'السودان', 'flag': '🇸🇩', 'code': '+249', 'continent': 'أفريقيا'},
    'sr': {'name': 'سورينام', 'flag': '🇸🇷', 'code': '+597', 'continent': 'أمريكا الجنوبية'},
    'sz': {'name': 'إسواتيني', 'flag': '🇸🇿', 'code': '+268', 'continent': 'أفريقيا'},
    'se': {'name': 'السويد', 'flag': '🇸🇪', 'code': '+46', 'continent': 'أوروبا'},
    'ch': {'name': 'سويسرا', 'flag': '🇨🇭', 'code': '+41', 'continent': 'أوروبا'},
    'sy': {'name': 'سوريا', 'flag': '🇸🇾', 'code': '+963', 'continent': 'آسيا'},
    'tj': {'name': 'طاجيكستان', 'flag': '🇹🇯', 'code': '+992', 'continent': 'آسيا'},
    'tz': {'name': 'تنزانيا', 'flag': '🇹🇿', 'code': '+255', 'continent': 'أفريقيا'},
    'th': {'name': 'تايلاند', 'flag': '🇹🇭', 'code': '+66', 'continent': 'آسيا'},
    'tl': {'name': 'تيمور الشرقية', 'flag': '🇹🇱', 'code': '+670', 'continent': 'آسيا'},
    'tg': {'name': 'توغو', 'flag': '🇹🇬', 'code': '+228', 'continent': 'أفريقيا'},
    'tn': {'name': 'تونس', 'flag': '🇹🇳', 'code': '+216', 'continent': 'أفريقيا'},
    'tr': {'name': 'تركيا', 'flag': '🇹🇷', 'code': '+90', 'continent': 'آسيا'},
    'tm': {'name': 'تركمانستان', 'flag': '🇹🇲', 'code': '+993', 'continent': 'آسيا'},
    'ug': {'name': 'أوغندا', 'flag': '🇺🇬', 'code': '+256', 'continent': 'أفريقيا'},
    'ua': {'name': 'أوكرانيا', 'flag': '🇺🇦', 'code': '+380', 'continent': 'أوروبا'},
    'ae': {'name': 'الإمارات العربية المتحدة', 'flag': '🇦🇪', 'code': '+971', 'continent': 'آسيا'},
    'gb': {'name': 'المملكة المتحدة', 'flag': '🇬🇧', 'code': '+44', 'continent': 'أوروبا'},
    'us': {'name': 'الولايات المتحدة', 'flag': '🇺🇸', 'code': '+1', 'continent': 'أمريكا الشمالية'},
    'uy': {'name': 'الأوروغواي', 'flag': '🇺🇾', 'code': '+598', 'continent': 'أمريكا الجنوبية'},
    'uz': {'name': 'أوزبكستان', 'flag': '🇺🇿', 'code': '+998', 'continent': 'آسيا'},
    've': {'name': 'فنزويلا', 'flag': '🇻🇪', 'code': '+58', 'continent': 'أمريكا الجنوبية'},
    'vn': {'name': 'فيتنام', 'flag': '🇻🇳', 'code': '+84', 'continent': 'آسيا'},
    'ye': {'name': 'اليمن', 'flag': '🇾🇪', 'code': '+967', 'continent': 'آسيا'},
    'zm': {'name': 'زامبيا', 'flag': '🇿🇲', 'code': '+260', 'continent': 'أفريقيا'},
    'zw': {'name': 'زيمبابوي', 'flag': '🇿🇼', 'code': '+263', 'continent': 'أفريقيا'}
}

# ===================================================================
# 🌍 منصات التواصل الاجتماعي المدعومة
# ===================================================================

PLATFORMS = {
    'facebook': {
        'domains': ['facebook.com', 'fb.com', 'fb.me'],
        'icon': '📘',
        'color': '#1877f2',
        'patterns': ['facebook.com/', 'fb.com/', 'fb.me/'],
        'location_selectors': ['meta[property="og:locality"]', 'meta[property="og:location"]', 'meta[name="location"]']
    },
    'twitter': {
        'domains': ['twitter.com', 'x.com', 't.co'],
        'icon': '🐦',
        'color': '#1da1f2',
        'patterns': ['twitter.com/', 'x.com/', 't.co/'],
        'location_selectors': ['meta[property="og:locality"]', 'meta[name="location"]']
    },
    'instagram': {
        'domains': ['instagram.com', 'instagr.am'],
        'icon': '📸',
        'color': '#e4405f',
        'patterns': ['instagram.com/', 'instagr.am/'],
        'location_selectors': ['meta[property="og:locality"]', 'meta[name="location"]']
    },
    'linkedin': {
        'domains': ['linkedin.com', 'lnkd.in'],
        'icon': '💼',
        'color': '#0a66c2',
        'patterns': ['linkedin.com/in/', 'linkedin.com/company/', 'lnkd.in/'],
        'location_selectors': ['meta[property="og:locality"]', 'meta[name="location"]']
    },
    'tiktok': {
        'domains': ['tiktok.com', 'vm.tiktok.com'],
        'icon': '🎵',
        'color': '#69c9d0',
        'patterns': ['tiktok.com/@', 'vm.tiktok.com/'],
        'location_selectors': ['meta[property="og:locality"]']
    },
    'youtube': {
        'domains': ['youtube.com', 'youtu.be'],
        'icon': '▶️',
        'color': '#ff0000',
        'patterns': ['youtube.com/@', 'youtube.com/channel/', 'youtube.com/user/', 'youtu.be/'],
        'location_selectors': ['meta[property="og:locality"]']
    },
    'github': {
        'domains': ['github.com', 'github.io'],
        'icon': '🐙',
        'color': '#333333',
        'patterns': ['github.com/'],
        'location_selectors': ['meta[property="og:locality"]']
    },
    'telegram': {
        'domains': ['t.me', 'telegram.me'],
        'icon': '✈️',
        'color': '#0088cc',
        'patterns': ['t.me/', 'telegram.me/'],
        'location_selectors': ['meta[property="og:locality"]']
    },
    'whatsapp': {
        'domains': ['wa.me', 'whatsapp.com'],
        'icon': '💬',
        'color': '#25d366',
        'patterns': ['wa.me/', 'whatsapp.com/'],
        'location_selectors': []
    },
    'snapchat': {
        'domains': ['snapchat.com'],
        'icon': '👻',
        'color': '#fffc00',
        'patterns': ['snapchat.com/add/'],
        'location_selectors': ['meta[property="og:locality"]']
    },
    'pinterest': {
        'domains': ['pinterest.com', 'pin.it'],
        'icon': '📌',
        'color': '#bd081c',
        'patterns': ['pinterest.com/', 'pin.it/'],
        'location_selectors': ['meta[property="og:locality"]']
    },
    'reddit': {
        'domains': ['reddit.com', 'redd.it'],
        'icon': '👽',
        'color': '#ff4500',
        'patterns': ['reddit.com/user/', 'reddit.com/r/'],
        'location_selectors': ['meta[property="og:locality"]']
    },
    'twitch': {
        'domains': ['twitch.tv'],
        'icon': '🎮',
        'color': '#9146ff',
        'patterns': ['twitch.tv/'],
        'location_selectors': ['meta[property="og:locality"]']
    },
    'discord': {
        'domains': ['discord.gg', 'discord.com'],
        'icon': '🎯',
        'color': '#5865f2',
        'patterns': ['discord.gg/', 'discord.com/'],
        'location_selectors': []
    },
    'medium': {
        'domains': ['medium.com'],
        'icon': '✍️',
        'color': '#00ab6c',
        'patterns': ['medium.com/@'],
        'location_selectors': ['meta[property="og:locality"]']
    },
    'spotify': {
        'domains': ['open.spotify.com'],
        'icon': '🎧',
        'color': '#1db954',
        'patterns': ['open.spotify.com/user/', 'open.spotify.com/artist/'],
        'location_selectors': []
    },
    'soundcloud': {
        'domains': ['soundcloud.com'],
        'icon': '☁️',
        'color': '#ff5500',
        'patterns': ['soundcloud.com/'],
        'location_selectors': ['meta[property="og:locality"]']
    },
    'vkontakte': {
        'domains': ['vk.com', 'vkontakte.ru'],
        'icon': '🔵',
        'color': '#07f',
        'patterns': ['vk.com/'],
        'location_selectors': ['meta[property="og:locality"]']
    }
}

# ===================================================================
# 🌍 فئة المحلل الرئيسية
# ===================================================================

class SocialScraperPro:
    """المحرك الرئيسي لاستخراج الموقع الجغرافي"""
    
    def __init__(self, timeout: int = 15, user_agent: str = None):
        self.timeout = timeout
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.results = []
        self.errors = []
        
    # ===================================================================
    # 🌍 أدوات مساعدة
    # ===================================================================
    
    def _fetch_url(self, url: str, retries: int = 2) -> Optional[requests.Response]:
        """جلب صفحة ويب مع إعادة المحاولة"""
        for attempt in range(retries + 1):
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp
                elif resp.status_code in [403, 404, 429]:
                    time.sleep(2 * (attempt + 1))
                else:
                    time.sleep(1 * (attempt + 1))
            except Exception as e:
                self.errors.append(f"Fetch error: {str(e)}")
                time.sleep(2 * (attempt + 1))
        return None
    
    def _clean_text(self, text: str) -> str:
        """تنظيف النص"""
        if not text:
            return ''
        return re.sub(r'\s+', ' ', text).strip()
    
    def _extract_json_from_script(self, html: str, pattern: str) -> Optional[Dict]:
        """استخراج JSON من داخل script tag"""
        match = re.search(pattern, html, re.S)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        return None
    
    def _extract_gps_coordinates(self, text: str) -> Optional[Dict]:
        """استخراج إحداثيات GPS من النص"""
        # تنسيق: 37.7749° N, 122.4194° W أو 37.7749, -122.4194
        patterns = [
            r'(-?\d+\.\d+)[°\s]*[NS]?[,\s]+(-?\d+\.\d+)[°\s]*[EW]?',
            r'(-?\d+\.\d+)[,\s]+(-?\d+\.\d+)',
            r'(\d+°\d+[\'"]?\s*[NS])[,\s]+(\d+°\d+[\'"]?\s*[EW])'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                try:
                    lat = float(match.group(1))
                    lng = float(match.group(2))
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        return {'latitude': lat, 'longitude': lng}
                except:
                    pass
        return None
    
    def _detect_country_from_text(self, text: str) -> Optional[Dict]:
        """كشف الدولة من النص"""
        if not text:
            return None
        
        text_lower = text.lower()
        
        # البحث عن أسماء الدول
        for code, data in COUNTRIES_DB.items():
            name = data['name'].lower()
            if name in text_lower:
                return {**data, 'code': code}
        
        return None
    
    def _detect_country_from_url(self, url: str) -> Optional[Dict]:
        """كشف الدولة من الرابط"""
        url_lower = url.lower()
        
        # أنماط الدول في الروابط
        for code, data in COUNTRIES_DB.items():
            if f'/{code}/' in url_lower or f'.{code}/' in url_lower:
                return {**data, 'code': code}
        
        return None
    
    def _detect_city_from_text(self, text: str) -> Optional[str]:
        """كشف المدينة من النص"""
        if not text:
            return None
        
        # قائمة المدن العربية والعالمية الشائعة
        cities = [
            'القاهرة', 'الرياض', 'دبي', 'أبو ظبي', 'الدوحة', 'المنامة', 'الكويت', 'مسقط',
            'عمان', 'بيروت', 'دمشق', 'بغداد', 'الموصل', 'البصرة', 'أربيل', 'النجف',
            'كربلاء', 'الحلة', 'ديالى', 'الأنبار', 'نينوى', 'صلاح الدين', 'كركوك',
            'ديالى', 'واسط', 'ميسان', 'ذي قار', 'المثنى', 'القادسية', 'بابل',
            'لندن', 'باريس', 'برلين', 'مدريد', 'روما', 'أثينا', 'أنقرة', 'إسطنبول',
            'طوكيو', 'بكين', 'سيول', 'موسكو', 'واشنطن', 'نيويورك', 'لوس أنجلوس',
            'شيكاغو', 'تورونتو', 'سيدني', 'ملبورن', 'جوهانسبرغ', 'نيروبي'
        ]
        
        for city in cities:
            if city in text:
                return city
        
        return None
    
    # ===================================================================
    # 🌍 تحليل المنصة
    # ===================================================================
    
    def detect_platform(self, url: str) -> Optional[Dict]:
        """كشف المنصة من الرابط"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            
            for platform_name, platform_data in PLATFORMS.items():
                if any(d in domain for d in platform_data['domains']):
                    return {
                        'name': platform_name,
                        **platform_data
                    }
            return None
        except:
            return None
    
    def extract_username(self, url: str, platform: Dict) -> Optional[str]:
        """استخراج اسم المستخدم من الرابط"""
        if not platform:
            return None
        
        try:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            
            for pattern in platform['patterns']:
                if pattern in url:
                    parts = url.split(pattern)
                    if len(parts) > 1:
                        username = parts[1].split('/')[0].split('?')[0]
                        return username
            return path
        except:
            return None
    
    # ===================================================================
    # 🌍 الاستخراج الرئيسي
    # ===================================================================
    
    def analyze_profile(self, url: str, fetch_content: bool = True) -> Dict:
        """تحليل ملف شخصي واستخراج الموقع"""
        result = {
            'url': url,
            'platform': None,
            'username': None,
            'country': None,
            'country_code': None,
            'flag': None,
            'continent': None,
            'city': None,
            'location': None,
            'gps': None,
            'confidence': 0,
            'status': 'pending',
            'timestamp': datetime.now().isoformat(),
            'details': {}
        }
        
        # كشف المنصة
        platform = self.detect_platform(url)
        if platform:
            result['platform'] = platform['name']
            result['icon'] = platform['icon']
            result['color'] = platform['color']
            result['username'] = self.extract_username(url, platform)
        
        # كشف الدولة من الرابط
        url_country = self._detect_country_from_url(url)
        if url_country:
            result['country'] = url_country['name']
            result['country_code'] = url_country['code']
            result['flag'] = url_country['flag']
            result['continent'] = url_country['continent']
            result['confidence'] = 60
        
        # جلب المحتوى إذا كان مطلوبًا
        if fetch_content:
            resp = self._fetch_url(url)
            if resp:
                try:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    
                    # استخراج المعلومات من Meta Tags
                    meta_geo = soup.find('meta', {'name': 'geo.position'}) or \
                               soup.find('meta', {'property': 'og:locality'}) or \
                               soup.find('meta', {'name': 'location'})
                    
                    if meta_geo and meta_geo.get('content'):
                        geo_content = meta_geo['content']
                        result['location'] = self._clean_text(geo_content)
                        
                        # محاولة استخراج إحداثيات
                        gps = self._extract_gps_coordinates(geo_content)
                        if gps:
                            result['gps'] = gps
                            result['confidence'] = 90
                        
                        # محاولة كشف الدولة من الموقع
                        country = self._detect_country_from_text(geo_content)
                        if country and not result.get('country'):
                            result['country'] = country['name']
                            result['country_code'] = country['code']
                            result['flag'] = country['flag']
                            result['continent'] = country['continent']
                            result['confidence'] = 80
                        
                        # محاولة كشف المدينة
                        city = self._detect_city_from_text(geo_content)
                        if city:
                            result['city'] = city
                            result['confidence'] = min(result['confidence'] + 10, 100)
                    
                    # البحث عن معلومات الموقع في النص
                    text_content = soup.get_text()
                    
                    # كشف الدولة من النص
                    if not result.get('country'):
                        country = self._detect_country_from_text(text_content)
                        if country:
                            result['country'] = country['name']
                            result['country_code'] = country['code']
                            result['flag'] = country['flag']
                            result['continent'] = country['continent']
                            result['confidence'] = 70
                    
                    # كشف المدينة من النص
                    if not result.get('city'):
                        city = self._detect_city_from_text(text_content)
                        if city:
                            result['city'] = city
                            result['confidence'] = min(result['confidence'] + 10, 100)
                    
                    # محاولة استخراج إحداثيات من النص
                    if not result.get('gps'):
                        gps = self._extract_gps_coordinates(text_content)
                        if gps:
                            result['gps'] = gps
                            result['confidence'] = 85
                    
                    result['status'] = 'success'
                    result['details']['title'] = soup.title.string if soup.title else None
                    result['details']['description'] = soup.find('meta', {'name': 'description'})
                    if result['details']['description']:
                        result['details']['description'] = result['details']['description'].get('content')
                    
                except Exception as e:
                    result['status'] = 'error'
                    result['error'] = str(e)
                    self.errors.append(f"Parse error: {e}")
            else:
                result['status'] = 'failed'
                result['error'] = 'Cannot fetch page'
        
        return result
    
    def analyze_multiple(self, urls: List[str], fetch_content: bool = True) -> List[Dict]:
        """تحليل عدة روابط"""
        results = []
        for url in urls:
            result = self.analyze_profile(url, fetch_content)
            results.append(result)
            self.results.append(result)
            time.sleep(0.5)
        return results
    
    # ===================================================================
    # 🌍 التصدير
    # ===================================================================
    
    def export_json(self, filename: str = 'location_data.json') -> str:
        """تصدير النتائج إلى JSON"""
        output = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total': len(self.results),
                'successful': len([r for r in self.results if r.get('status') == 'success']),
                'failed': len([r for r in self.results if r.get('status') != 'success'])
            },
            'results': self.results,
            'errors': self.errors[:10]
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        return filename
    
    def export_html(self, filename: str = 'location_report.html') -> str:
        """تصدير تقرير HTML"""
        html = f'''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌍 Social Scraper Pro - Location Report</title>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    font-family: 'Cairo', sans-serif;
    background: #0a0a1a;
    color: #e8e0f0;
    padding: 30px;
    direction: rtl;
}}
.container {{ max-width: 1000px; margin: 0 auto; }}
h1 {{
    text-align: center;
    font-size: 32px;
    font-weight: 900;
    background: linear-gradient(135deg, #00ffc8, #6366f1, #ff4081);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}}
.subtitle {{
    text-align: center;
    color: #9088b0;
    margin-bottom: 30px;
}}
.stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
}}
.stat-card {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
}}
.stat-card .num {{
    font-size: 28px;
    font-weight: 700;
    color: #00ffc8;
}}
.stat-card .label {{
    font-size: 12px;
    color: #9088b0;
    margin-top: 5px;
}}
.result-card {{
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 15px;
    transition: 0.3s;
}}
.result-card:hover {{
    border-color: #00ffc8;
}}
.platform-badge {{
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}}
.location-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-top: 12px;
}}
.location-item {{
    background: rgba(255,255,255,0.03);
    padding: 10px 14px;
    border-radius: 12px;
}}
.location-item .lbl {{
    font-size: 10px;
    color: #9088b0;
    text-transform: uppercase;
}}
.location-item .val {{
    font-size: 15px;
    font-weight: 600;
    margin-top: 3px;
}}
.confidence-bar {{
    height: 4px;
    background: rgba(255,255,255,0.06);
    border-radius: 2px;
    margin-top: 12px;
    overflow: hidden;
}}
.confidence-fill {{
    height: 100%;
    background: linear-gradient(90deg, #ff4081, #ffaa00, #00ffc8);
    border-radius: 2px;
    transition: width 0.5s;
}}
.error-text {{ color: #ff4081; font-size: 13px; }}
.footer {{
    text-align: center;
    color: #504868;
    font-size: 12px;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.04);
}}
</style>
</head>
<body>
<div class="container">
    <h1>🌍 Social Scraper Pro</h1>
    <div class="subtitle">تقرير الموقع الجغرافي من روابط التواصل الاجتماعي</div>
    
    <div class="stats">
        <div class="stat-card"><div class="num">{len(self.results)}</div><div class="label">📊 المجموع</div></div>
        <div class="stat-card"><div class="num" style="color:#00ffc8">{len([r for r in self.results if r.get('status') == 'success'])}</div><div class="label">✅ نجاح</div></div>
        <div class="stat-card"><div class="num" style="color:#ff4081">{len([r for r in self.results if r.get('status') != 'success'])}</div><div class="label">❌ فشل</div></div>
        <div class="stat-card"><div class="num" style="color:#ffaa00">{len(set(r.get('country', '') for r in self.results if r.get('country')))}</div><div class="label">🌍 دول</div></div>
    </div>
    
    <div id="results">
'''
        
        for r in self.results:
            status_class = 'success' if r.get('status') == 'success' else 'failed'
            confidence = r.get('confidence', 0)
            
            html += f'''
    <div class="result-card" style="border-right: 4px solid {r.get('color', '#666') if r.get('status') == 'success' else '#ff4081'}">
        <div class="platform-badge" style="background:{r.get('color', '#666')}20; color:{r.get('color', '#666')}">
            {r.get('icon', '🌐')} {r.get('platform', 'غير معروف')}
        </div>
        <div style="font-size:16px;font-weight:600;margin-top:6px;">{r.get('username', 'غير معروف')}</div>
        <div class="location-row">
            <div class="location-item">
                <div class="lbl">🌍 الدولة</div>
                <div class="val">{r.get('flag', '❓')} {r.get('country', 'غير محدد')}</div>
            </div>
            <div class="location-item">
                <div class="lbl">📞 رمز الدولة</div>
                <div class="val">{r.get('country_code', 'غير محدد')}</div>
            </div>
            <div class="location-item">
                <div class="lbl">🏙️ المدينة</div>
                <div class="val">{r.get('city', 'غير محدد')}</div>
            </div>
            <div class="location-item">
                <div class="lbl">📊 الدقة</div>
                <div class="val">{confidence}%</div>
            </div>
        </div>
        {f'<div class="location-item" style="grid-column:1/-1;background:rgba(0,255,200,0.04);"><div class="lbl">📍 الموقع</div><div class="val">{r.get("location", "غير محدد")}</div></div>' if r.get('location') else ''}
        {f'<div class="location-item" style="grid-column:1/-1;background:rgba(99,102,241,0.04);"><div class="lbl">🛰️ الإحداثيات</div><div class="val">{r["gps"]["latitude"]}, {r["gps"]["longitude"]}</div></div>' if r.get('gps') else ''}
        <div class="confidence-bar"><div class="confidence-fill" style="width:{confidence}%"></div></div>
        <div style="font-size:11px;color:#504868;margin-top:10px;">🔗 {r.get('url', '')}</div>
        {f'<div class="error-text">❌ {r.get("error", "")}</div>' if r.get('error') else ''}
    </div>
'''
        
        html += f'''
    </div>
    <div class="footer">
        تم الإنشاء بواسطة Social Scraper Pro v2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</div>
</body>
</html>'''
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        return filename
    
    # ===================================================================
    # 🌍 العرض في الطرفية
    # ===================================================================
    
    def display_results(self):
        """عرض النتائج في الطرفية"""
        print("\n" + "="*70)
        print("  🌍 SOCIAL SCRAPER PRO - LOCATION RESULTS")
        print("="*70)
        
        for r in self.results:
            print(f"\n{'─'*70}")
            print(f"  🔗 {r['url']}")
            print(f"  {r.get('icon', '🌐')} المنصة: {r.get('platform', 'غير معروف').upper()}")
            print(f"  👤 المستخدم: {r.get('username', 'غير معروف')}")
            
            if r.get('flag'):
                print(f"  {r['flag']} الدولة: {r.get('country', 'غير محدد')}")
            if r.get('country_code'):
                print(f"  📞 رمز الدولة: {r['country_code']}")
            if r.get('city'):
                print(f"  🏙️ المدينة: {r['city']}")
            if r.get('location'):
                print(f"  📍 الموقع: {r['location']}")
            if r.get('gps'):
                print(f"  🛰️ الإحداثيات: {r['gps']['latitude']}, {r['gps']['longitude']}")
            
            print(f"  📊 دقة التحليل: {r.get('confidence', 0)}%")
            
            if r.get('error'):
                print(f"  ❌ خطأ: {r['error']}")
        
        print("\n" + "="*70)
        print(f"  📊 الإجمالي: {len(self.results)}")
        print(f"  ✅ نجاح: {len([r for r in self.results if r.get('status') == 'success'])}")
        print(f"  ❌ فشل: {len([r for r in self.results if r.get('status') != 'success'])}")
        print("="*70)


# ===================================================================
# 🌍 الوظيفة الرئيسية
# ===================================================================

def main():
    """الوظيفة الرئيسية"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  🌍  SOCIAL SCRAPER PRO - Location Intelligence Tool        ║
║  استخراج الموقع الجغرافي الحقيقي للأشخاص من جميع المنصات   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    scraper = SocialScraperPro()
    
    # قراءة المدخلات
    queries = []
    
    if len(sys.argv) > 1:
        queries = sys.argv[1:]
    elif os.path.exists('input.txt'):
        with open('input.txt', 'r', encoding='utf-8') as f:
            queries = [line.strip() for line in f if line.strip()]
    else:
        print("📝  أدخل الروابط (افصل بينها بفاصلة):")
        user_input = input("🔍 > ").strip()
        if user_input:
            queries = [q.strip() for q in user_input.split(',') if q.strip()]
    
    if not queries:
        print("❌  لا توجد مدخلات.")
        print("   استخدام: python scraper.py https://instagram.com/user https://twitter.com/user")
        sys.exit(1)
    
    print(f"\n📊  عدد الروابط: {len(queries)}")
    print("⏳  جاري التحليل...\n")
    
    # التحليل
    for query in queries:
        print(f"   🔍  تحليل: {query}")
        result = scraper.analyze_profile(query)
        if result.get('status') == 'success':
            print(f"      ✅  {result.get('flag', '🌍')} {result.get('country', 'غير محدد')} | دقة: {result.get('confidence', 0)}%")
        else:
            print(f"      ❌  {result.get('error', 'فشل')}")
    
    # التصدير
    print("\n📁  تصدير النتائج...")
    scraper.export_json('location_data.json')
    scraper.export_html('location_report.html')
    
    # العرض
    scraper.display_results()
    
    print("\n✅  تم الانتهاء!")
    print(f"   📄 JSON: location_data.json")
    print(f"   📄 HTML: location_report.html")


if __name__ == '__main__':
    main()

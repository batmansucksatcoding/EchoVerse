# emotions/emotion_analyzer.py
import os
import re
import json
from typing import Dict, Any, Optional, List, Tuple
from collections import Counter

# transformers used for local fallback
from transformers import pipeline

# requests used for optional HF Inference API remote JSON generation
import requests

# Environment configuration
HF_API_KEY = os.getenv("HF_API_KEY")
HF_EMOTION_MODEL = os.getenv("HF_EMOTION_MODEL", "google/flan-t5-small")


class EmotionLexicon:
    """
    Comprehensive emotion lexicon with intensity weights and contextual patterns.
    Maps words, phrases, and patterns to emotions with varying intensities.
    """
    
    EMOTION_LEXICON = {
        'joy': {
            'high': [
                'ecstatic', 'euphoric', 'overjoyed', 'elated', 'jubilant', 'thrilled',
                'exuberant', 'exhilarated', 'radiant', 'glowing', 'beaming', 'gleeful',
                'rapturous', 'blissful', 'heavenly', 'divine', 'magnificent', 'triumphant',
                'victorious', 'celebratory', 'festive', 'joyous', 'merry', 'jolly',
                'flying high', 'on cloud nine', 'over the moon', 'walking on air',
                'bursting with joy', 'couldn\'t be happier', 'best day ever',
                'living my best life', 'pure happiness', 'absolute bliss'
            ],
            'medium_high': [
                'happy', 'delighted', 'pleased', 'cheerful', 'content', 'satisfied',
                'glad', 'grateful', 'thankful', 'blessed', 'fortunate', 'lucky',
                'wonderful', 'fantastic', 'amazing', 'great', 'excellent', 'superb',
                'lovely', 'beautiful', 'perfect', 'ideal', 'brilliant', 'marvelous',
                'splendid', 'terrific', 'fabulous', 'spectacular', 'outstanding',
                'delightful', 'charming', 'pleasant', 'enjoyable', 'gratifying',
                'rewarding', 'fulfilling', 'heartwarming', 'uplifting', 'inspiring',
                'smile', 'smiling', 'grinning', 'laughing', 'giggling', 'chuckling',
                'bright', 'sunny', 'glorious', 'golden', 'shining', 'sparkling',
                'makes me happy', 'fills me with joy', 'brings me happiness'
            ],
            'medium': [
                'good', 'nice', 'fine', 'alright', 'okay', 'decent', 'fair',
                'positive', 'optimistic', 'hopeful', 'upbeat', 'lighthearted',
                'carefree', 'easygoing', 'relaxed', 'comfortable', 'at ease',
                'peaceful', 'calm', 'serene', 'tranquil', 'harmonious',
                'sweet', 'warm', 'cozy', 'homey', 'welcoming', 'friendly',
                'kind', 'gentle', 'tender', 'loving', 'caring', 'affectionate',
                'amusing', 'entertaining', 'fun', 'playful', 'silly', 'goofy',
                'relief', 'relieved', 'better', 'improved', 'recovering', 'healing'
            ],
            'low': [
                'contented', 'peaceful', 'settled', 'stable', 'balanced', 'centered',
                'grounded', 'composed', 'collected', 'level', 'even', 'steady',
                'mild pleasure', 'slight happiness', 'somewhat pleased', 'fairly content'
            ]
        },
        
        'sadness': {
            'high': [
                'devastated', 'heartbroken', 'crushed', 'shattered', 'destroyed',
                'anguished', 'tormented', 'despairing', 'hopeless', 'helpless',
                'grief-stricken', 'bereaved', 'mourning', 'grieving', 'lamenting',
                'inconsolable', 'distraught', 'traumatized', 'broken', 'ruined',
                'torn apart', 'ripped apart', 'falling apart', 'can\'t go on',
                'don\'t want to live', 'life is meaningless', 'world is ending',
                'unbearable pain', 'drowning in sorrow', 'consumed by grief',
                'lost everything', 'nothing left', 'completely empty', 'totally broken',
                'soul-crushing', 'life-shattering', 'world-ending', 'devastating blow'
            ],
            'medium_high': [
                'depressed', 'depression', 'miserable', 'wretched', 'woeful',
                'melancholy', 'melancholic', 'sorrowful', 'mournful', 'doleful',
                'gloomy', 'dismal', 'dreary', 'bleak', 'dark', 'black', 'gray',
                'forlorn', 'dejected', 'downcast', 'crestfallen', 'despondent',
                'low', 'down', 'blue', 'glum', 'morose', 'sullen', 'somber',
                'tearful', 'weeping', 'crying', 'sobbing', 'bawling', 'wailing',
                'heavy-hearted', 'broken-hearted', 'heavy heart', 'aching heart',
                'can\'t stop crying', 'tears won\'t stop', 'crying myself to sleep',
                'feel like crying', 'want to cry', 'need to cry', 'holding back tears'
            ],
            'medium': [
                'sad', 'unhappy', 'upset', 'disappointed', 'let down', 'discouraged',
                'disheartened', 'dismayed', 'downhearted', 'dispirited',
                'hurt', 'wounded', 'pained', 'aching', 'suffering', 'hurting',
                'lonely', 'alone', 'isolated', 'abandoned', 'forsaken', 'forgotten',
                'empty', 'hollow', 'void', 'vacant', 'barren', 'desolate',
                'numb', 'deadened', 'lifeless', 'spiritless', 'apathetic',
                'tired', 'weary', 'worn out', 'exhausted', 'drained', 'depleted',
                'miss', 'missing', 'longing', 'yearning', 'pining', 'aching for',
                'regret', 'regretful', 'remorseful', 'guilty', 'ashamed',
                'loss', 'losing', 'lost', 'gone', 'left', 'departed', 'passed away'
            ],
            'low': [
                'wistful', 'nostalgic', 'pensive', 'reflective', 'contemplative',
                'subdued', 'muted', 'quiet', 'withdrawn', 'reserved', 'distant',
                'resigned', 'accepting', 'surrendering', 'giving up',
                'sigh', 'sighing', 'heavy sigh', 'deep breath',
                'slightly sad', 'a bit down', 'somewhat unhappy', 'little blue'
            ]
        },
        
        'anger': {
            'high': [
                'furious', 'enraged', 'livid', 'incensed', 'infuriated', 'irate',
                'seething', 'raging', 'fuming', 'boiling', 'volcanic', 'explosive',
                'outraged', 'incandescent', 'apoplectic', 'ballistic', 'berserk',
                'seeing red', 'blood boiling', 'losing my mind', 'about to explode',
                'want to scream', 'want to hit something', 'want to break things',
                'can\'t control my anger', 'blinded by rage', 'consumed by fury',
                'absolutely livid', 'utterly furious', 'completely enraged',
                'violently angry', 'dangerously angry', 'murderous rage'
            ],
            'medium_high': [
                'angry', 'mad', 'pissed', 'pissed off', 'ticked off', 'fed up',
                'heated', 'inflamed', 'hot-headed', 'hot-tempered', 'fiery',
                'aggravated', 'exasperated', 'infuriated', 'provoked', 'goaded',
                'resentful', 'bitter', 'hostile', 'antagonistic', 'combative',
                'aggressive', 'confrontational', 'belligerent', 'pugnacious',
                'indignant', 'offended', 'insulted', 'affronted', 'slighted',
                'steaming', 'flustered', 'worked up', 'riled up', 'fired up',
                'makes me angry', 'pisses me off', 'drives me crazy', 'makes me mad'
            ],
            'medium': [
                'annoyed', 'irritated', 'frustrated', 'bothered', 'irked', 'vexed',
                'agitated', 'ruffled', 'perturbed', 'displeased', 'dissatisfied',
                'cross', 'grumpy', 'cranky', 'grouchy', 'crabby', 'surly',
                'moody', 'temperamental', 'snappy', 'short-tempered', 'impatient',
                'unjust', 'unfair', 'wrong', 'bullshit', 'ridiculous', 'absurd',
                'disgusting behavior', 'unacceptable', 'intolerable', 'outrageous',
                'disrespect', 'disrespected', 'insulted', 'degraded', 'humiliated'
            ],
            'low': [
                'upset', 'miffed', 'put off', 'put out', 'disgruntled',
                'disappointed', 'let down', 'dissatisfied', 'unhappy',
                'testy', 'touchy', 'sensitive', 'defensive',
                'slightly annoyed', 'a bit irritated', 'somewhat frustrated'
            ]
        },
        
        'fear': {
            'high': [
                'terrified', 'petrified', 'horrified', 'traumatized', 'terrorized',
                'panicked', 'panic-stricken', 'terror-stricken', 'paralyzed with fear',
                'frozen', 'immobilized', 'rooted to the spot', 'can\'t move',
                'nightmare', 'nightmarish', 'hellish', 'harrowing', 'horrifying',
                'bone-chilling', 'blood-curdling', 'hair-raising', 'spine-tingling',
                'scared to death', 'frightened to death', 'scared out of my mind',
                'heart pounding', 'heart racing', 'can\'t breathe', 'gasping',
                'dread', 'dreading', 'impending doom', 'sense of doom',
                'going to die', 'fear for my life', 'life in danger', 'mortal fear'
            ],
            'medium_high': [
                'scared', 'afraid', 'frightened', 'fearful', 'scared stiff',
                'alarmed', 'startled', 'shocked', 'shaken', 'rattled', 'unnerved',
                'threatened', 'endangered', 'at risk', 'in danger', 'unsafe',
                'vulnerable', 'exposed', 'unprotected', 'defenseless', 'helpless',
                'insecure', 'uncertain', 'unsure', 'doubtful', 'hesitant',
                'timid', 'timorous', 'meek', 'shy', 'bashful', 'cowering',
                'quaking', 'trembling', 'shaking', 'shivering', 'quivering',
                'terrifying', 'scary', 'spooky', 'creepy', 'eerie', 'sinister'
            ],
            'medium': [
                'worried', 'concerned', 'troubled', 'bothered', 'disturbed',
                'apprehensive', 'uneasy', 'unsettled', 'uncomfortable', 'edgy',
                'nervous', 'jittery', 'jumpy', 'skittish', 'twitchy', 'on edge',
                'tense', 'strained', 'stressed', 'pressured', 'overwhelmed',
                'phobia', 'phobic', 'irrational fear', 'intense fear',
                'nightmare', 'bad dream', 'haunted', 'plagued', 'tormented',
                'paranoid', 'suspicious', 'distrustful', 'wary', 'guarded'
            ],
            'low': [
                'cautious', 'careful', 'vigilant', 'watchful', 'alert',
                'hesitant', 'reluctant', 'unwilling', 'resistant',
                'slightly worried', 'a bit concerned', 'somewhat nervous'
            ]
        },
        
        'love': {
            'high': [
                'adore', 'adoring', 'worship', 'worshiping', 'idolize',
                'devoted', 'devoted to', 'dedication', 'commitment', 'loyalty',
                'passionate', 'passionately in love', 'burning passion', 'intense love',
                'infatuated', 'smitten', 'enamored', 'besotted', 'captivated',
                'enchanted', 'spellbound', 'mesmerized', 'enthralled', 'bewitched',
                'madly in love', 'deeply in love', 'head over heels', 'crazy about',
                'can\'t live without', 'complete me', 'my everything', 'my world',
                'soul mate', 'true love', 'love of my life', 'meant to be',
                'unconditional love', 'eternal love', 'forever love', 'everlasting',
                'my heart belongs to', 'gave my heart', 'stole my heart'
            ],
            'medium_high': [
                'love', 'loving', 'in love', 'fall in love', 'fell in love',
                'beloved', 'lover', 'sweetheart', 'darling', 'honey', 'dear',
                'baby', 'babe', 'angel', 'treasure', 'precious', 'priceless',
                'cherish', 'cherished', 'treasured', 'valued', 'prized',
                'affection', 'affectionate', 'tender', 'tenderness', 'warmth',
                'devotion', 'devoted', 'faithful', 'loyal', 'true', 'steadfast',
                'caring', 'nurturing', 'protective', 'supportive', 'understanding',
                'intimate', 'intimacy', 'close', 'closeness', 'connection', 'bond',
                'romance', 'romantic', 'romantically', 'candlelit', 'moonlight',
                'kiss', 'kissing', 'embrace', 'embracing', 'hug', 'hugging',
                'cuddle', 'cuddling', 'snuggle', 'snuggling', 'hold', 'holding'
            ],
            'medium': [
                'fond', 'fondness', 'attached', 'attachment', 'connected',
                'attraction', 'attracted', 'drawn to', 'pulled toward',
                'admire', 'admiration', 'respect', 'esteem', 'regard',
                'appreciate', 'appreciation', 'grateful for', 'thankful for',
                'endearment', 'endearing', 'sweet', 'sweetness', 'cute',
                'gentle', 'soft', 'kind', 'kindness', 'compassion', 'empathy',
                'sentimental', 'heartfelt', 'sincere', 'genuine', 'authentic',
                'chemistry', 'spark', 'connection', 'vibe', 'energy',
                'miss you', 'missing you', 'think of you', 'thinking of you'
            ],
            'low': [
                'like', 'liking', 'enjoy', 'enjoying', 'pleased with',
                'interest', 'interested', 'curious about', 'intrigued by',
                'crush', 'crushing', 'fancy', 'fancy you', 'into you',
                'somewhat fond', 'slightly attached', 'a bit attracted'
            ]
        },
        
        'anxiety': {
            'high': [
                'panic', 'panicking', 'panic attack', 'full-blown panic',
                'overwhelmed', 'drowning', 'suffocating', 'can\'t breathe',
                'spiraling', 'spinning out', 'losing control', 'out of control',
                'breakdown', 'breaking down', 'falling apart', 'coming undone',
                'paralyzed', 'frozen', 'trapped', 'stuck', 'cornered', 'boxed in',
                'racing thoughts', 'mind racing', 'can\'t think straight', 'foggy',
                'hyperventilating', 'heart pounding', 'chest tight', 'dizzy',
                'catastrophizing', 'worst case scenario', 'everything\'s going wrong',
                'can\'t cope', 'can\'t handle', 'too much', 'unbearable',
                'terrifying anxiety', 'crippling anxiety', 'debilitating anxiety'
            ],
            'medium_high': [
                'anxious', 'anxiety', 'stressed', 'stressed out', 'stress',
                'tense', 'tension', 'wound up', 'tight', 'rigid', 'stiff',
                'on edge', 'edge of my seat', 'walking on eggshells', 'treading carefully',
                'frazzled', 'frantic', 'frenetic', 'feverish', 'hectic',
                'desperate', 'desperation', 'urgency', 'pressing', 'critical',
                'pressured', 'pressure', 'burdened', 'burden', 'weight', 'heavy',
                'weighed down', 'crushed', 'squeezed', 'compressed', 'constricted',
                'dread', 'dreading', 'impending', 'looming', 'approaching doom',
                'sleepless', 'insomnia', 'can\'t sleep', 'lying awake', 'tossing turning',
                'sweating', 'shaking', 'trembling', 'quivering', 'jittery'
            ],
            'medium': [
                'nervous', 'nervousness', 'worried', 'worry', 'worrying',
                'concerned', 'concern', 'uneasy', 'restless', 'fidgety',
                'agitated', 'unsettled', 'disturbed', 'troubled', 'bothered',
                'preoccupied', 'distracted', 'scattered', 'unfocused', 'lost',
                'uncertain', 'uncertainty', 'unsure', 'doubtful', 'questioning',
                'hesitant', 'hesitation', 'reluctant', 'unwilling', 'resistant',
                'apprehensive', 'wary', 'cautious', 'guarded', 'careful',
                'butterflies', 'stomach churning', 'nauseous', 'queasy', 'sick',
                'overthinking', 'overanalyzing', 'ruminating', 'obsessing', 'fixating'
            ],
            'low': [
                'slightly anxious', 'a bit nervous', 'somewhat worried',
                'mildly concerned', 'little uneasy', 'touch of anxiety',
                'edge', 'edgy', 'antsy', 'jumpy', 'twitchy'
            ]
        },
        
        'excitement': {
            'high': [
                'ecstatic', 'euphoric', 'exhilarated', 'thrilled', 'electrified',
                'pumped', 'pumped up', 'hyped', 'hyped up', 'amped', 'amped up',
                'stoked', 'psyched', 'fired up', 'revved up', 'charged up',
                'buzzing', 'electric', 'explosive', 'dynamic', 'kinetic',
                'adrenaline rush', 'adrenaline pumping', 'blood pumping',
                'can\'t contain myself', 'bursting with excitement', 'beside myself',
                'on fire', 'lit', 'fired up', 'burning with excitement',
                'incredible', 'unbelievable', 'mind-blowing', 'jaw-dropping',
                'best thing ever', 'amazing opportunity', 'dream come true'
            ],
            'medium_high': [
                'excited', 'excitement', 'enthusiastic', 'enthusiasm', 'zeal',
                'eager', 'eagerness', 'keen', 'passionate', 'passion', 'fervor',
                'energized', 'energy', 'vigor', 'vitality', 'vibrancy',
                'animated', 'lively', 'spirited', 'vivacious', 'bubbly',
                'effervescent', 'sparkling', 'radiant', 'glowing', 'beaming',
                'dynamic', 'vibrant', 'exuberant', 'ebullient', 'bouncy',
                'can\'t wait', 'counting down', 'anticipation', 'looking forward',
                'thrilling', 'exhilarating', 'electrifying', 'invigorating'
            ],
            'medium': [
                'interested', 'interest', 'curious', 'curiosity', 'intrigued',
                'engaged', 'engagement', 'involved', 'invested', 'committed',
                'motivated', 'motivation', 'driven', 'determined', 'focused',
                'inspired', 'inspiration', 'stimulated', 'aroused', 'awakened',
                'alert', 'attentive', 'aware', 'conscious', 'mindful',
                'ready', 'prepared', 'primed', 'set', 'geared up'
            ],
            'low': [
                'anticipating', 'hopeful', 'optimistic', 'positive',
                'upbeat', 'cheerful', 'bright', 'sunny',
                'slightly excited', 'a bit eager', 'somewhat interested'
            ]
        },
        
        'surprise': {
            'high': [
                'shocked', 'stunned', 'astounded', 'astonished', 'amazed',
                'flabbergasted', 'dumbfounded', 'speechless', 'gobsmacked',
                'mind-blown', 'blown away', 'floored', 'staggered', 'stupefied',
                'awestruck', 'thunderstruck', 'shell-shocked', 'bowled over',
                'jaw dropped', 'eyes wide', 'can\'t believe it', 'unbelievable',
                'never expected', 'didn\'t see coming', 'out of nowhere',
                'completely unexpected', 'total surprise', 'utter shock'
            ],
            'medium_high': [
                'surprised', 'surprise', 'startled', 'jolted', 'jarred',
                'taken aback', 'caught off guard', 'caught by surprise',
                'blindsided', 'sideswiped', 'ambushed', 'unprepared',
                'unexpected', 'unforeseen', 'unanticipated', 'unpredicted',
                'sudden', 'abrupt', 'sharp', 'quick', 'rapid', 'swift',
                'wow', 'whoa', 'oh my god', 'omg', 'what', 'no way'
            ],
            'medium': [
                'curious', 'wondering', 'puzzled', 'perplexed', 'confused',
                'bewildered', 'baffled', 'mystified', 'confounded', 'stumped',
                'intrigued', 'fascinated', 'captivated', 'entranced', 'absorbed',
                'discovery', 'revelation', 'epiphany', 'realization', 'insight'
            ],
            'low': [
                'noticed', 'realized', 'discovered', 'found', 'learned',
                'understood', 'figured out', 'uncovered', 'revealed',
                'slightly surprised', 'a bit unexpected', 'somewhat startled'
            ]
        },
        
        'disgust': {
            'high': [
                'revolted', 'repulsed', 'repelled', 'sickened', 'nauseated',
                'appalled', 'horrified', 'disgusted', 'abhorred', 'detested',
                'loathed', 'despised', 'hated', 'can\'t stand', 'makes me sick',
                'want to vomit', 'want to throw up', 'gag', 'gagging', 'retching',
                'stomach turning', 'bile rising', 'makes my skin crawl',
                'utterly repulsive', 'absolutely disgusting', 'completely vile',
                'morally reprehensible', 'ethically wrong', 'deeply offensive'
            ],
            'medium_high': [
                'gross', 'grossed out', 'nasty', 'foul', 'vile', 'repugnant',
                'offensive', 'obnoxious', 'repellent', 'distasteful', 'unpleasant',
                'rotten', 'putrid', 'rank', 'stinking', 'reeking', 'fetid',
                'filthy', 'dirty', 'grimy', 'slimy', 'squalid', 'seedy',
                'sleazy', 'creepy', 'skeevy', 'sketchy', 'shady', 'dodgy',
                'revolting', 'repulsive', 'hideous', 'grotesque', 'monstrous'
            ],
            'medium': [
                'dislike', 'don\'t like', 'disapprove', 'disapproval', 'disdain',
                'averse', 'aversion', 'opposed', 'against', 'anti',
                'turned off', 'put off', 'off-putting', 'unappetizing',
                'uncomfortable', 'uneasy', 'bothered', 'disturbed',
                'wrong', 'bad', 'inappropriate', 'improper', 'unsuitable',
                'tacky', 'tasteless', 'vulgar', 'crude', 'crass', 'coarse'
            ],
            'low': [
                'unimpressed', 'underwhelmed', 'disappointed', 'let down',
                'dissatisfied', 'displeased', 'unhappy', 'not happy',
                'slightly disgusted', 'a bit gross', 'somewhat off-putting'
            ]
        },
        
        'neutral': {
            'high': [
                'indifferent', 'apathetic', 'uninterested', 'disinterested',
                'detached', 'disconnected', 'removed', 'distant', 'aloof',
                'uninvolved', 'uncommitted', 'disengaged', 'withdrawn',
                'impartial', 'neutral', 'objective', 'unbiased', 'balanced',
                'don\'t care', 'whatever', 'doesn\'t matter', 'who cares',
                'meh', 'so-so', 'mediocre', 'neither here nor there'
            ],
            'medium_high': [
                'neutral', 'balanced', 'even', 'level', 'steady', 'stable',
                'constant', 'consistent', 'regular', 'routine', 'standard',
                'normal', 'typical', 'usual', 'ordinary', 'common', 'average',
                'mundane', 'everyday', 'humdrum', 'run-of-the-mill',
                'unremarkable', 'unexceptional', 'nondescript', 'plain'
            ],
            'medium': [
                'okay', 'fine', 'alright', 'all right', 'decent', 'fair',
                'moderate', 'medium', 'middling', 'adequate', 'sufficient',
                'acceptable', 'tolerable', 'bearable', 'passable',
                'nothing special', 'not bad', 'could be worse'
            ],
            'low': [
                'calm', 'peaceful', 'quiet', 'still', 'tranquil', 'serene',
                'placid', 'composed', 'collected', 'poised', 'centered',
                'level-headed', 'rational', 'reasonable', 'sensible', 'practical',
                'matter-of-fact', 'straightforward', 'simple', 'basic'
            ]
        }
    }
    
    # Contextual phrases that modify emotion intensity
    INTENSIFIERS = {
        'very': 1.3,
        'extremely': 1.5,
        'incredibly': 1.5,
        'absolutely': 1.4,
        'completely': 1.4,
        'totally': 1.4,
        'utterly': 1.5,
        'thoroughly': 1.3,
        'deeply': 1.4,
        'profoundly': 1.5,
        'intensely': 1.5,
        'overwhelmingly': 1.6,
        'unbearably': 1.6,
        'impossibly': 1.5,
        'unbelievably': 1.5,
        'ridiculously': 1.4,
        'insanely': 1.5,
        'crazy': 1.3,
        'super': 1.2,
        'really': 1.2,
        'quite': 1.1,
        'rather': 1.1,
        'pretty': 1.1,
        'fairly': 1.05,
        'somewhat': 0.8,
        'slightly': 0.6,
        'barely': 0.5,
        'hardly': 0.5,
        'a little': 0.7,
        'a bit': 0.7,
        'kind of': 0.8,
        'sort of': 0.8
    }
    
    # Negation words that flip emotion
    NEGATIONS = [
        'not', 'no', 'never', 'neither', 'nor', 'none', 'nobody', 'nothing',
        'nowhere', 'hardly', 'scarcely', 'barely', "n't", 'without', 'lack'
    ]
    
    @classmethod
    def get_intensity_weight(cls, intensity_level: str) -> float:
        """Convert intensity level to numeric weight"""
        weights = {
            'high': 1.0,
            'medium_high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        return weights.get(intensity_level, 0.5)
    
    @classmethod
    def analyze_with_context(cls, text: str) -> Dict[str, float]:
        """
        Advanced lexicon-based analysis with context awareness.
        Returns emotion scores considering intensifiers, negations, and word proximity.
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        emotion_scores = {
            'joy': 0.0, 'sadness': 0.0, 'anger': 0.0, 'fear': 0.0,
            'love': 0.0, 'anxiety': 0.0, 'excitement': 0.0,
            'surprise': 0.0, 'disgust': 0.0, 'neutral': 0.0
        }
        
        for i, word in enumerate(words):
            # Check for emotion words
            for emotion, intensity_dict in cls.EMOTION_LEXICON.items():
                for intensity_level, word_list in intensity_dict.items():
                    if word in word_list or any(w in word for w in word_list):
                        base_score = cls.get_intensity_weight(intensity_level)
                        
                        # Check for intensifiers in previous 3 words
                        intensifier_multiplier = 1.0
                        for j in range(max(0, i-3), i):
                            if words[j] in cls.INTENSIFIERS:
                                intensifier_multiplier *= cls.INTENSIFIERS[words[j]]
                        
                        # Check for negations in previous 3 words
                        is_negated = False
                        for j in range(max(0, i-3), i):
                            if words[j] in cls.NEGATIONS or words[j].endswith("n't"):
                                is_negated = True
                                break
                        
                        # Apply score
                        if is_negated:
                            # Negation inverts or reduces the emotion
                            base_score *= 0.3  # Reduced impact when negated
                        else:
                            base_score *= intensifier_multiplier
                        
                        emotion_scores[emotion] += min(base_score, 1.0)
        
        # Normalize scores
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {k: v / total for k, v in emotion_scores.items()}
        else:
            emotion_scores['neutral'] = 1.0
        
        return emotion_scores


class HybridEmotionAnalyzer:
    """
    Enhanced Hybrid Emotion Analyzer with comprehensive lexicon support
    """

    EMOTIONS = [
        'joy', 'sadness', 'anger', 'fear', 'surprise',
        'disgust', 'neutral', 'love', 'anxiety', 'excitement'
    ]

    def __init__(self, prefer_remote: bool = False, use_enhanced_lexicon: bool = True):
        """
        prefer_remote: if True and HF_API_KEY exists -> try remote JSON generation first.
        use_enhanced_lexicon: if True, blend lexicon analysis with ML models for better accuracy
        """
        self.prefer_remote = prefer_remote and bool(HF_API_KEY)
        self.use_enhanced_lexicon = use_enhanced_lexicon

        # Initialize local pipelines (may download models)
        try:
            self.emotion_pipe = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True,
                top_k=None
            )
        except Exception as e:
            print(f"⚠️ Could not load emotion pipeline: {e}")
            self.emotion_pipe = None

        try:
            self.sentiment_pipe = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
        except Exception as e:
            print(f"⚠️ Could not load sentiment pipeline: {e}")
            self.sentiment_pipe = None

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Enhanced analysis flow with lexicon blending
        """
        text = (text or "").strip()
        if not text:
            return self._get_default_analysis()

        result = None

        # Try remote JSON first if preferred
        if self.prefer_remote:
            try:
                resp_text = self._remote_json_response(text)
                parsed = self._parse_response(resp_text)
                if parsed:
                    result = parsed
            except Exception as e:
                print(f"Remote JSON analysis failed, falling back: {e}")

        # If no remote result, try local analysis
        if result is None:
            try:
                result = self._local_analysis(text)
            except Exception as e:
                print(f"Local analysis failed: {e}")
                result = self._enhanced_keyword_analysis(text)

        # Blend with lexicon analysis if enabled
        if self.use_enhanced_lexicon:
            try:
                lexicon_scores = EmotionLexicon.analyze_with_context(text)
                result = self._blend_analyses(result, lexicon_scores, ml_weight=0.6, lexicon_weight=0.4)
            except Exception as e:
                print(f"Lexicon blending failed: {e}")

        # Apply contextual booster
        try:
            result = self._contextual_emotion_boost(text, result)
        except Exception as e:
            print(f"Contextual booster failed: {e}")

        return self._ensure_proper_floats(result)

    def _blend_analyses(self, ml_result: Dict[str, Any], lexicon_scores: Dict[str, float],
                       ml_weight: float = 0.6, lexicon_weight: float = 0.4) -> Dict[str, Any]:
        """
        Intelligently blend ML model predictions with lexicon-based analysis
        """
        blended = {}
        
        for emotion in self.EMOTIONS:
            ml_score = ml_result.get(emotion, 0.0)
            lex_score = lexicon_scores.get(emotion, 0.0)
            
            # Weighted average
            blended[emotion] = (ml_score * ml_weight) + (lex_score * lexicon_weight)
        
        # Recalculate primary emotion
        primary_emotion = max(blended.items(), key=lambda x: x[1])
        
        blended.update({
            'primary_emotion': primary_emotion[0],
            'primary_emotion_score': primary_emotion[1],
            'sentiment_polarity': ml_result.get('sentiment_polarity', 0.0)
        })
        
        return blended

    def _local_analysis(self, text: str) -> Dict[str, Any]:
        """Enhanced local analysis with better normalization"""
        scores = {e: 0.0 for e in self.EMOTIONS}

        if self.emotion_pipe is not None:
            try:
                raw = self.emotion_pipe(text[:512])
                if isinstance(raw, list) and len(raw) > 0:
                    if isinstance(raw[0], list):
                        raw = raw[0]

                    label_mapping = {
                        'joy': 'joy', 'happiness': 'joy',
                        'sadness': 'sadness', 'sad': 'sadness',
                        'anger': 'anger', 'angry': 'anger',
                        'fear': 'fear', 'scared': 'fear',
                        'surprise': 'surprise',
                        'disgust': 'disgust',
                        'neutral': 'neutral',
                        'love': 'love',
                    }

                    total_score = 0.0
                    for item in raw:
                        label = item.get("label", "").lower()
                        score = float(item.get("score", 0.0))
                        mapped = label_mapping.get(label, label)
                        if mapped in scores:
                            scores[mapped] += score
                            total_score += score

                    if total_score > 0:
                        for emo in scores:
                            scores[emo] = scores[emo] / total_score

            except Exception as e:
                print(f"emotion_pipe error: {e}")

        # Derive complex emotions
        scores['anxiety'] = min((scores['fear'] * 0.7 + scores['sadness'] * 0.3), 1.0)
        scores['excitement'] = min((scores['joy'] * 0.5 + scores['surprise'] * 0.5), 1.0)

        # Get sentiment
        polarity = 0.0
        if self.sentiment_pipe is not None:
            try:
                sent_result = self.sentiment_pipe(text[:512])[0]
                score = float(sent_result.get("score", 0.0))
                label = sent_result.get("label", "").lower()
                if "neg" in label:
                    polarity = -score
                elif "pos" in label:
                    polarity = score
            except Exception as e:
                print(f"sentiment_pipe error: {e}")

        base_emotions = {k: v for k, v in scores.items() if k not in ['anxiety', 'excitement']}
        primary_emotion = max(base_emotions.items(), key=lambda x: x[1])

        result = {k: float(v) for k, v in scores.items()}
        result.update({
            "primary_emotion": primary_emotion[0],
            "primary_emotion_score": float(primary_emotion[1]),
            "sentiment_polarity": float(polarity),
        })

        return result

    def _enhanced_keyword_analysis(self, text: str) -> Dict[str, Any]:
        """Enhanced keyword analysis using the comprehensive lexicon"""
        scores = EmotionLexicon.analyze_with_context(text)
        
        # Calculate sentiment from emotion scores
        positive_emotions = ['joy', 'love', 'excitement']
        negative_emotions = ['sadness', 'anger', 'fear', 'anxiety', 'disgust']
        
        pos_score = sum(scores.get(e, 0.0) for e in positive_emotions)
        neg_score = sum(scores.get(e, 0.0) for e in negative_emotions)
        
        sentiment = (pos_score - neg_score) / (pos_score + neg_score) if (pos_score + neg_score) > 0 else 0.0
        
        primary = max(scores.items(), key=lambda x: x[1])
        
        result = {k: float(v) for k, v in scores.items()}
        result.update({
            "primary_emotion": primary[0],
            "primary_emotion_score": float(primary[1]),
            "sentiment_polarity": float(sentiment)
        })
        
        return result

    def _contextual_emotion_boost(self, text: str, emotion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced contextual booster with more sophisticated rules"""
        if not isinstance(emotion_data, dict):
            return emotion_data

        text_lower = text.lower()
        
        # Detect emotional complexity patterns
        mixed_patterns = {
            'bittersweet': (('love', 0.2), ('sadness', 0.2), ('joy', 0.15)),
            'melancholic_peace': (('sadness', 0.2), ('neutral', 0.15)),
            'anxious_excitement': (('anxiety', 0.2), ('excitement', 0.2)),
            'loving_fear': (('love', 0.2), ('fear', 0.15)),
            'angry_sadness': (('anger', 0.2), ('sadness', 0.2)),
        }
        
        # Check for complex emotional patterns
        if any(word in text_lower for word in ['but', 'however', 'yet', 'although', 'despite']):
            # Text contains contrasts - boost multiple emotions slightly
            for pattern_name, boosts in mixed_patterns.items():
                pattern_words = {
                    'bittersweet': ['bittersweet', 'sweet sorrow', 'happy sad', 'joy and pain'],
                    'melancholic_peace': ['peaceful sadness', 'calm melancholy', 'quiet sadness'],
                    'anxious_excitement': ['nervous excitement', 'anxiously excited', 'worried but excited'],
                    'loving_fear': ['scared to love', 'fear of losing', 'terrified of love'],
                    'angry_sadness': ['angry and hurt', 'furious and sad', 'mad and disappointed']
                }
                
                if any(phrase in text_lower for phrase in pattern_words.get(pattern_name, [])):
                    for emotion, boost in boosts:
                        emotion_data[emotion] = min(1.0, emotion_data.get(emotion, 0.0) + boost)
        
        # Recompute primary after boosts
        base_emotions = {k: v for k, v in emotion_data.items() 
                        if k in self.EMOTIONS and k not in ['anxiety', 'excitement']}
        primary = max(base_emotions.items(), key=lambda x: x[1])
        emotion_data["primary_emotion"] = primary[0]
        emotion_data["primary_emotion_score"] = primary[1]

        return emotion_data

    # Keep all other methods from original implementation
    def _remote_json_response(self, text: str) -> str:
        if not HF_API_KEY:
            raise RuntimeError("HUGGINGFACE_API_KEY not configured")
        prompt = self._build_analysis_prompt(text)
        url = f"https://api-inference.huggingface.co/models/{HF_EMOTION_MODEL}"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {
            "inputs": prompt,
            "options": {"wait_for_model": True},
            "parameters": {"max_new_tokens": 512, "temperature": 0.0}
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and isinstance(data[0], dict) and 'generated_text' in data[0]:
            return data[0]['generated_text']
        if isinstance(data, dict) and data.get('generated_text'):
            return data.get('generated_text')
        return json.dumps(data)

    def _build_analysis_prompt(self, text: str) -> str:
        return f"""Analyze the emotional content of the following journal entry. 
Return ONLY a valid JSON object with no additional text, markdown, or explanation.

Analyze these emotions: joy, sadness, anger, fear, surprise, disgust, neutral, love, anxiety, excitement

For each emotion, provide a score from 0.0 to 1.0 (as decimal, NOT percentage) indicating how strongly that emotion is present.
Also determine:
- primary_emotion: The strongest emotion
- primary_emotion_score: The confidence score for the primary emotion (0.0 to 1.0)
- sentiment_polarity: Overall sentiment from -1.0 (very negative) to 1.0 (very positive)

Journal entry:
{text}

Return format:
{{
    "joy": 0.0,
    "sadness": 0.0,
    "anger": 0.0,
    "fear": 0.0,
    "surprise": 0.0,
    "disgust": 0.0,
    "neutral": 0.0,
    "love": 0.0,
    "anxiety": 0.0,
    "excitement": 0.0,
    "primary_emotion": "emotion_name",
    "primary_emotion_score": 0.0,
    "sentiment_polarity": 0.0
}}"""

    def _parse_response(self, response: str) -> Optional[Dict[str, Any]]:
        if not response:
            return None
        text = response.strip()
        if text.startswith("```") and text.endswith("```"):
            text = text[3:-3].strip()
        text = re.sub(r"^```json\s*", "", text, flags=re.I).strip()
        json_text = self._extract_first_json(text)
        if not json_text:
            try:
                return json.loads(text)
            except Exception:
                return None
        try:
            obj = json.loads(json_text)
        except json.JSONDecodeError:
            alt = json_text.replace("'", '"')
            try:
                obj = json.loads(alt)
            except Exception:
                return None
        if not self._validate_analysis(obj):
            return None
        return obj

    def _extract_first_json(self, text: str) -> Optional[str]:
        """Extracts the first valid JSON object substring from text."""
        start = None
        depth = 0
        for i, ch in enumerate(text):
            if ch == '{':
                if start is None:
                    start = i
                depth += 1
            elif ch == '}':
                if depth > 0:
                    depth -= 1
                    if depth == 0 and start is not None:
                        return text[start:i+1]
        return None

    def _validate_analysis(self, obj: Dict[str, Any]) -> bool:
        """Check if parsed JSON has valid emotion analysis structure."""
        if not isinstance(obj, dict):
            return False
        required_fields = [
            'joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust',
            'neutral', 'love', 'anxiety', 'excitement',
            'primary_emotion', 'primary_emotion_score', 'sentiment_polarity'
        ]
        for field in required_fields:
            if field not in obj:
                return False
        return True

    def _ensure_proper_floats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert all numeric values in data to floats safely."""
        clean_data = {}
        for k, v in data.items():
            try:
                if isinstance(v, (int, float)):
                    clean_data[k] = float(v)
                elif isinstance(v, str) and re.match(r"^-?\d+(\.\d+)?$", v.strip()):
                    clean_data[k] = float(v.strip())
                else:
                    clean_data[k] = v
            except Exception:
                clean_data[k] = 0.0
        return clean_data

    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return a neutral default emotion analysis."""
        base = {emo: 0.0 for emo in self.EMOTIONS}
        base.update({
            "primary_emotion": "neutral",
            "primary_emotion_score": 1.0,
            "sentiment_polarity": 0.0
        })
        return base

# Compatibility alias for Django imports
EmotionAnalyzer = HybridEmotionAnalyzer


# ✅ Optional: Helper function for quick testing
if __name__ == "__main__":
    analyzer = HybridEmotionAnalyzer(prefer_remote=False)
    text = "I was nervous but also excited to start something new. It felt bittersweet leaving behind old memories."
    result = analyzer.analyze_text(text)
    print(json.dumps(result, indent=2))

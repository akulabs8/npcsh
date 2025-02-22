import random
from typing import Dict, Any, List
import json
import uuid
from npcsh.stream import get_anthropic_stream, process_anthropic_tool_stream

import json


class MockToolKit:
    """
    A collection of mock tools that demonstrate tool use without external APIs
    """

    @staticmethod
    def generate_character_profile(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a random character profile based on input parameters

        Args:
            params (dict): Parameters for character generation
                - profession (optional): Specify a profession
                - age_range (optional): Specify an age range

        Returns:
            dict: A generated character profile
        """
        # Predefined default values
        professions = [
            "Wizard",
            "Knight",
            "Archer",
            "Merchant",
            "Scholar",
            "Blacksmith",
            "Farmer",
            "Sailor",
        ]

        ages = {
            "child": (6, 12),
            "teen": (13, 19),
            "young_adult": (20, 35),
            "adult": (36, 50),
            "elder": (51, 70),
        }

        # Use provided profession or infer from context
        profession = params.get("profession")
        if not profession:
            if "wizard" in params.get("context", "").lower():
                profession = "Wizard"
            else:
                profession = random.choice(professions)

        # Use provided age range or infer from context
        age_range = params.get("age_range")
        if not age_range:
            if "young adult" in params.get("context", "").lower():
                age_range = "young_adult"
            else:
                age_range = random.choice(list(ages.keys()))

        # Calculate age
        age_min, age_max = ages[age_range]
        age = random.randint(age_min, age_max)

        # Generate skills
        skills = random.sample(
            [
                "Sword Fighting",
                "Magic",
                "Archery",
                "Diplomacy",
                "Crafting",
                "Healing",
                "Navigation",
                "Survival",
            ],
            k=random.randint(2, 4),
        )

        return {
            "id": str(uuid.uuid4()),
            "name": f"{random.choice(['Aria', 'Kai', 'Lyra', 'Rowan', 'Sage', 'Quinn'])} {random.choice(['Stormwind', 'Blackwood', 'Silverlight', 'Nightshade'])}",
            "profession": profession,
            "age": age,
            "skills": skills,
            "backstory_seed": random.choice(
                [
                    "Orphaned at a young age",
                    "Seeking revenge",
                    "Driven by curiosity",
                    "Following a mysterious prophecy",
                    "Escaping a troubled past",
                ]
            ),
        }

    @staticmethod
    def roll_dice(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate dice rolling with various configurations

        Args:
            params (dict): Dice roll parameters
                - num_dice (int): Number of dice to roll
                - sides (int): Number of sides on each die

        Returns:
            dict: Dice roll results
        """
        num_dice = params.get("num_dice", 1)
        sides = params.get("sides", 6)

        rolls = [random.randint(1, sides) for _ in range(num_dice)]

        return {
            "rolls": rolls,
            "total": sum(rolls),
            "num_dice": num_dice,
            "dice_type": f"d{sides}",
        }

    @staticmethod
    def generate_story_prompt(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a random story prompt or writing exercise

        Args:
            params (dict): Optional parameters to guide prompt generation
                - genre (optional): Specify a story genre
                - complexity (optional): Complexity of the prompt

        Returns:
            dict: A generated story prompt
        """
        genres = [
            "Fantasy",
            "Science Fiction",
            "Mystery",
            "Historical Fiction",
            "Horror",
            "Romance",
        ]

        prompts = {
            "simple": [
                "Write about a character who finds a mysterious object.",
                "Describe a journey that changes everything.",
                "Tell a story that begins with an unexpected arrival.",
            ],
            "complex": [
                "Create a narrative that explores the consequences of a single decision across multiple timelines.",
                "Write a story where the protagonist's greatest strength is also their fatal flaw.",
                "Develop a tale that interweaves three seemingly unrelated characters' lives.",
            ],
        }

        genre = params.get("genre", random.choice(genres))
        complexity = params.get("complexity", random.choice(["simple", "complex"]))

        return {
            "genre": genre,
            "complexity": complexity,
            "prompt": random.choice(prompts[complexity]),
            "additional_constraints": random.sample(
                [
                    "Must include a talking animal",
                    "Story must be told in reverse chronological order",
                    "No dialogue allowed",
                    "Include exactly three plot twists",
                ],
                k=random.randint(0, 2),
            ),
        }


tools = [
    {
        "name": "generate_character_profile",
        "description": "Generate a random character profile with optional constraints",
        "input_schema": {
            "type": "object",
            "properties": {
                "profession": {
                    "type": "string",
                    "description": "Optional specific profession",
                },
                "age_range": {
                    "type": "string",
                    "enum": ["child", "teen", "young_adult", "adult", "elder"],
                    "description": "Optional age range",
                },
            },
        },
    },
    {
        "name": "roll_dice",
        "description": "Simulate dice rolls with configurable parameters",
        "input_schema": {
            "type": "object",
            "properties": {
                "num_dice": {
                    "type": "integer",
                    "description": "Number of dice to roll",
                },
                "sides": {
                    "type": "integer",
                    "description": "Number of sides on each die",
                },
            },
        },
    },
    {
        "name": "generate_story_prompt",
        "description": "Create a random story writing prompt",
        "input_schema": {
            "type": "object",
            "properties": {
                "genre": {"type": "string", "description": "Optional story genre"},
                "complexity": {
                    "type": "string",
                    "enum": ["simple", "complex"],
                    "description": "Complexity of the story prompt",
                },
            },
        },
    },
]

# Prepare messages with example tool use requests
messages = [
    {
        "role": "user",
        "content": "Can you generate a character for a fantasy story? Maybe a young adult wizard.",
    },
    {"role": "user", "content": "Now roll some dice for me - how about 3d20?"},
    {
        "role": "user",
        "content": "Give me an interesting story prompt for a science fiction story.",
    },
]

# Custom tool map
tool_map = {
    "generate_character_profile": MockToolKit.generate_character_profile,
    "roll_dice": MockToolKit.roll_dice,
    "generate_story_prompt": MockToolKit.generate_story_prompt,
}


# Stream the response with tools
stream = get_anthropic_stream(
    messages=messages,
    model="claude-3-5-haiku-latest",
    tools=tools,
    tool_choice={"type": "any"},
)


tool_results = process_anthropic_tool_stream(stream, tool_map)

# Print out the tool results with more context
print("Tool Execution Results:")
for result in tool_results:
    print(f"\n--- {result['tool_name'].replace('_', ' ').title()} ---")
    print("Tool Input:", result.get("tool_input", "No specific input"))
    print("Execution Result:")
    for key, value in result["tool_result"].items():
        print(f"  {key}: {value}")

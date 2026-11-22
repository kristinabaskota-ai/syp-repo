"""
RareRoot - Database Seeder
NOTE: All import rules, treatment safety flags, and plant health data are SAMPLE DATA
for educational and demonstration purposes. In a production environment, regulatory
rules and medical/horticultural safety should be verified with official biosecurity
authorities and certified horticulturists.
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import (
    User, Category, Product, ImportRule, Symptom, Treatment, WantedRequest, Offer
)
from app.security import get_password_hash


def seed_database(db: Session) -> None:
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Check if database already has categories (to avoid re-seeding)
    if db.query(Category).first():
        return

    # 1. Categories
    categories_data = [
        {"name": "Rare", "description": "Highly sought-after, variegated, and collectible botanical specimens."},
        {"name": "Indoor", "description": "Air-purifying foliage, shade lovers, and low-light apartment plants."},
        {"name": "Seasonal", "description": "Flowering beauties and annuals adapted to seasonal weather transitions."},
        {"name": "Tree", "description": "Fruit-bearing, timber, ornamental, and shade tree saplings for landscaping."},
        {"name": "Treatment", "description": "Organic, non-chemical, and eco-friendly plant remedies and health essentials."}
    ]
    categories = {}
    for cat in categories_data:
        c = Category(**cat)
        db.add(c)
        db.flush()
        categories[c.name] = c

    # 2. Demo Users
    # Admin: admin@rareroot.com / Admin@12345
    admin_user = User(
        email="admin@rareroot.com",
        full_name="RareRoot Administrator",
        hashed_password=get_password_hash("Admin@12345"),
        role="admin",
        is_active=True,
        is_approved=True
    )
    # Seller: seller@rareroot.com / Seller@12345
    seller_user = User(
        email="seller@rareroot.com",
        full_name="Himalayan Flora Nursery",
        hashed_password=get_password_hash("Seller@12345"),
        role="seller",
        is_active=True,
        is_approved=True
    )
    # Buyer: buyer@rareroot.com / Buyer@12345
    buyer_user = User(
        email="buyer@rareroot.com",
        full_name="Aarav Sharma",
        hashed_password=get_password_hash("Buyer@12345"),
        role="buyer",
        is_active=True,
        is_approved=True
    )
    db.add_all([admin_user, seller_user, buyer_user])
    db.flush()

    # 3. Realistic Products (~24 products)
    products_data = [
        # Rare Category
        {
            "seller_id": seller_user.id,
            "category_id": categories["Rare"].id,
            "name": "Monstera Albo Variegata",
            "description": "Exquisite white-and-green chimera foliage with high sectoral contrast. Highly prized collectors aroid in a 6-inch pot.",
            "price": 18500.0,
            "stock": 4,
            "light_requirement": "bright",
            "pet_safe": False,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1614594975525-e45190c55d0b?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Rare"].id,
            "name": "Philodendron Pink Princess",
            "description": "Deep burgundy foliage splashed with vibrant bubblegum pink sectoral patterns. Established, actively growing root system.",
            "price": 4200.0,
            "stock": 8,
            "light_requirement": "medium",
            "pet_safe": False,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1628178122971-61b2b80459a9?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Rare"].id,
            "name": "Anthurium Clarinervium",
            "description": "Velvety heart-shaped dark emerald leaves accented with striking white veins. Native to southern Mexico rocky outcrops.",
            "price": 6500.0,
            "stock": 5,
            "light_requirement": "medium",
            "pet_safe": False,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1616046229478-9901c5536a45?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Rare"].id,
            "name": "Stephania Erecta (Caudex)",
            "description": "Geometric round umbrella leaves sprouting gracefully from a woody potato-like caudex bulb. Unique architectural beauty.",
            "price": 3800.0,
            "stock": 6,
            "light_requirement": "bright",
            "pet_safe": False,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1598880940371-c756e015fea1?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Rare"].id,
            "name": "Alocasia Baginda 'Silver Dragon'",
            "description": "Textured metallic silver-green shield leaves with contrasting dark hunter-green veining. Compact jewel alocasia.",
            "price": 2900.0,
            "stock": 7,
            "light_requirement": "medium",
            "pet_safe": False,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Rare"].id,
            "name": "Hoya Carnosa 'Compacta' Variegated",
            "description": "Contorted Hindu Rope vine featuring creamy pink margins on tightly curled succulent leaves. Pet friendly wax plant.",
            "price": 3400.0,
            "stock": 10,
            "light_requirement": "bright",
            "pet_safe": True,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1545241047-6083a3684587?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        # Indoor Category
        {
            "seller_id": seller_user.id,
            "category_id": categories["Indoor"].id,
            "name": "Calathea Orbifolia",
            "description": "Broad round leaves marked with silvery brushstrokes. Non-toxic, air-purifying, pet-safe prayer plant.",
            "price": 1800.0,
            "stock": 12,
            "light_requirement": "medium",
            "pet_safe": True,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1509423350716-97f9360b4e09?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Indoor"].id,
            "name": "Sansevieria Trifasciata (Snake Plant)",
            "description": "Hardy architectural upright spear plant. Extremely drought tolerant, excellent for bedrooms and low-light corners.",
            "price": 950.0,
            "stock": 25,
            "light_requirement": "low",
            "pet_safe": False,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1599598425947-320e8b15d0fa?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Indoor"].id,
            "name": "Zamioculcas Zamiifolia (ZZ Plant)",
            "description": "Glossy emerald foliage storing moisture in thick rhizomes. Survives neglect, dim offices, and infrequent watering.",
            "price": 1250.0,
            "stock": 20,
            "light_requirement": "low",
            "pet_safe": False,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1632306230491-0e785501b870?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Indoor"].id,
            "name": "Chlorophytum Comosum (Spider Plant)",
            "description": "Arching green and cream striped foliage producing charming baby plantlets. Certified pet-safe and air scrubbing.",
            "price": 600.0,
            "stock": 30,
            "light_requirement": "bright",
            "pet_safe": True,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1572688484438-313a6e50c333?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Indoor"].id,
            "name": "Peace Lily (Spathiphyllum)",
            "description": "Graceful dark leaves topped with pure white spathes. Natural humidity indicator and renowned indoor toxin filter.",
            "price": 1100.0,
            "stock": 15,
            "light_requirement": "low",
            "pet_safe": False,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1593691509543-c55fb32e7355?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Indoor"].id,
            "name": "Peperomia Obtusifolia (Baby Rubber Plant)",
            "description": "Thick succulent leaves on compact stems. Extremely easy to care for and completely safe for inquisitive cats and dogs.",
            "price": 850.0,
            "stock": 18,
            "light_requirement": "medium",
            "pet_safe": True,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1512428559087-560fa5ceab42?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        # Seasonal Category
        {
            "seller_id": seller_user.id,
            "category_id": categories["Seasonal"].id,
            "name": "Himalayan Blue Poppy (Meconopsis)",
            "description": "Legendary true-sky-blue petals surrounding golden stamens. Native to alpine meadows of the Himalayas.",
            "price": 1400.0,
            "stock": 14,
            "light_requirement": "medium",
            "pet_safe": True,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Seasonal"].id,
            "name": "Poinsettia (Euphorbia Pulcherrima)",
            "description": "Crimson red bracts bringing joyful winter festive color. Popular holiday potted plant.",
            "price": 750.0,
            "stock": 22,
            "light_requirement": "bright",
            "pet_safe": False,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Seasonal"].id,
            "name": "Marigold (Sayapatri - Tagetes erecta)",
            "description": "Aromatic golden-orange blossoms essential for Tihar celebrations and natural organic garden pest deterrence.",
            "price": 350.0,
            "stock": 40,
            "light_requirement": "full-sun",
            "pet_safe": True,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Seasonal"].id,
            "name": "Cyclamen Persicum (Winter Bloom)",
            "description": "Upswept magenta blooms rising above frosted marbled foliage during cool winter months.",
            "price": 1200.0,
            "stock": 11,
            "light_requirement": "medium",
            "pet_safe": False,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1508615039623-a25605d2b022?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        # Tree Category (with tree_purpose)
        {
            "seller_id": seller_user.id,
            "category_id": categories["Tree"].id,
            "name": "Himalayan Cedar (Deodar - Cedrus deodara)",
            "description": "Majestic evergreen conifer native to western Himalayas. Valued for rot-resistant aromatic timber and sacred temples.",
            "price": 2800.0,
            "stock": 9,
            "light_requirement": "full-sun",
            "pet_safe": True,
            "tree_purpose": "timber",
            "image_url": "https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Tree"].id,
            "name": "Nepali Paulownia (Kiri Tree)",
            "description": "Ultra fast-growing lightweight hardwood tree producing purple bell blooms. Premium sustainable timber candidate.",
            "price": 1950.0,
            "stock": 15,
            "light_requirement": "full-sun",
            "pet_safe": True,
            "tree_purpose": "timber",
            "image_url": "https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Tree"].id,
            "name": "Golden Champak (Michelia Champaca)",
            "description": "Fragrant golden-orange blossoms famous in Nepal for Joy perfume and traditional offerings. Stately ornamental tree.",
            "price": 2400.0,
            "stock": 8,
            "light_requirement": "full-sun",
            "pet_safe": True,
            "tree_purpose": "ornamental",
            "image_url": "https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Tree"].id,
            "name": "Dwarf Mango 'Amrapali' (Mangifera indica)",
            "description": "Grafted compact mango tree yielding sweet, fiberless aromatic orange pulp. Thrives in warm garden plots or large containers.",
            "price": 3200.0,
            "stock": 7,
            "light_requirement": "full-sun",
            "pet_safe": True,
            "tree_purpose": "fruit",
            "image_url": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Tree"].id,
            "name": "Gulmohar (Royal Poinciana - Delonix regia)",
            "description": "Sprawling umbrella canopy with feathery fern-like leaves and blazing orange-scarlet flowers. Exceptional urban shade.",
            "price": 2100.0,
            "stock": 6,
            "light_requirement": "full-sun",
            "pet_safe": False,
            "tree_purpose": "shade",
            "image_url": "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        # Treatment Category (Products linked to Treatments)
        {
            "seller_id": seller_user.id,
            "category_id": categories["Treatment"].id,
            "name": "Pure Cold-Pressed Neem Oil (250ml)",
            "description": "100% natural cold-pressed azadirachtin oil for controlling mites, thrips, aphids, and whiteflies. Safe for pets and edible herbs.",
            "price": 650.0,
            "stock": 35,
            "light_requirement": "low",
            "pet_safe": True,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Treatment"].id,
            "name": "Potassium Bicarbonate Bio-Fungicide",
            "description": "Food-grade organic contact fungicide that prevents and eradicates powdery mildew, black spot, and leaf blights.",
            "price": 850.0,
            "stock": 25,
            "light_requirement": "low",
            "pet_safe": True,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Treatment"].id,
            "name": "Organic Insecticidal Soap Spray (500ml)",
            "description": "Gentle potassium salts of fatty acids. Dissolves protective cuticle of soft-bodied garden insects without chemical residues.",
            "price": 550.0,
            "stock": 30,
            "light_requirement": "low",
            "pet_safe": True,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1585751119414-ef2636f8aede?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Treatment"].id,
            "name": "Systemic Copper Fungicide Spray (500ml)",
            "description": "Broad-spectrum copper octanoate protection against anthracnose, stem cankers, and severe blights. Keep away from domestic pets.",
            "price": 920.0,
            "stock": 18,
            "light_requirement": "low",
            "pet_safe": False,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        },
        {
            "seller_id": seller_user.id,
            "category_id": categories["Treatment"].id,
            "name": "Bio-Enzymatic Root Rot Drench & Reviver (300ml)",
            "description": "Beneficial mycorrhizae and Trichoderma fungi inoculant that consumes decomposing roots and establishes protective root shields.",
            "price": 1150.0,
            "stock": 16,
            "light_requirement": "low",
            "pet_safe": True,
            "tree_purpose": None,
            "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=80",
            "is_active": True
        }
    ]

    products_by_name = {}
    for p_data in products_data:
        prod = Product(**p_data)
        db.add(prod)
        db.flush()
        products_by_name[prod.name] = prod

    # 4. Plant Doctor Symptoms and Treatments (~10 symptoms, 3-5 treatments each)
    neem_prod = products_by_name["Pure Cold-Pressed Neem Oil (250ml)"]
    fungicide_bio = products_by_name["Potassium Bicarbonate Bio-Fungicide"]
    soap_prod = products_by_name["Organic Insecticidal Soap Spray (500ml)"]
    copper_prod = products_by_name["Systemic Copper Fungicide Spray (500ml)"]
    root_prod = products_by_name["Bio-Enzymatic Root Rot Drench & Reviver (300ml)"]

    symptoms_data = [
        {
            "plant_part": "leaf",
            "observation": "Yellowing leaves with dry, brown crispy edges",
            "diagnosis": "Low Humidity and Under-watering Stress",
            "cause": "Cellular dehydration from dry indoor heating, irregular watering intervals, or low ambient humidity below 40%.",
            "treatments": [
                {
                    "name": "Pebble Tray & Deep Bottom Soak",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Place pot over a shallow tray filled with pebbles and water (pot bottom must not touch water). Immerse pot in room-temperature water for 25 minutes until topsoil is damp.",
                    "product_id": None
                },
                {
                    "name": "Cold-Pressed Neem Foliar Hydration & Gloss",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Mist foliage with micro-diluted Neem Oil emulsified in distilled water to seal leaf transpirational moisture.",
                    "product_id": neem_prod.id
                },
                {
                    "name": "Sterile Leaf Margin Trimming",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Trim purely brown necrotic tissue with 70% alcohol-wiped scissors, leaving a tiny sliver of brown to avoid cutting green living tissue.",
                    "product_id": None
                }
            ]
        },
        {
            "plant_part": "leaf",
            "observation": "White powdery coating and curling on upper leaf surface",
            "diagnosis": "Powdery Mildew (Erysiphales Fungal Spores)",
            "cause": "Poor air movement combined with moderate temperatures (15-27°C) and high nighttime relative humidity.",
            "treatments": [
                {
                    "name": "Potassium Bicarbonate Bio-Fungicide Spray",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Dissolve 1 rounded teaspoon in 1 liter of water. Spray top and underside of leaves thoroughly every 7 days until clear.",
                    "product_id": fungicide_bio.id
                },
                {
                    "name": "Baking Soda & Vegetable Oil Wash",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Mix 1 tbsp sodium bicarbonate and 1/2 tsp gentle vegetable oil into warm water. Apply in gentle indirect morning light.",
                    "product_id": None
                },
                {
                    "name": "Mechanical Air Circulation & Pruning",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Prune densely clustered interior leaves to promote airflow and position an oscillating fan 6 feet away on low.",
                    "product_id": None
                },
                {
                    "name": "Systemic Copper Fungicide Spray",
                    "treatment_type": "chemical",
                    "pet_safe": False,
                    "child_safe": False,
                    "edible_safe": False,
                    "instructions": "Apply copper octanoate formulation wearing gloves and mask. Keep pets and young children away from treated foliage until dry.",
                    "product_id": copper_prod.id
                }
            ]
        },
        {
            "plant_part": "leaf",
            "observation": "Fine webbing under leaves with yellow stippling dots",
            "diagnosis": "Spider Mite Infestation (Tetranychidae)",
            "cause": "Dry, arid indoor microclimates allow microscopic spider mites to rapidly colonize and drain chloroplast sap.",
            "treatments": [
                {
                    "name": "Organic Insecticidal Soap Folial Wash",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Coat leaf undersides thoroughly with insecticidal soap. Repeat every 4-5 days to break egg hatching cycles.",
                    "product_id": soap_prod.id
                },
                {
                    "name": "Pure Cold-Pressed Neem Oil Smother",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Mix 5ml Neem Oil and 2ml horticultural dish soap per liter of lukewarm water. Wipe foliage with a soft micro-cloth.",
                    "product_id": neem_prod.id
                },
                {
                    "name": "High Pressure Water Rinse Isolation",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Place plant in the shower or outdoors and direct a lukewarm pressurized water stream at the undersides of leaves.",
                    "product_id": None
                },
                {
                    "name": "Pyrethroid Chemical Contact Spray",
                    "treatment_type": "chemical",
                    "pet_safe": False,
                    "child_safe": False,
                    "edible_safe": False,
                    "instructions": "Aerosolized contact miticide. Use outdoors only. Highly toxic to aquatic life, felines, and beneficial insects.",
                    "product_id": None
                }
            ]
        },
        {
            "plant_part": "leaf",
            "observation": "Lower leaves turning pale yellow and dropping; soggy soil",
            "diagnosis": "Over-watering Induced Early Root Hypoxia",
            "cause": "Excess moisture filling air pores in soil, suffocating feeder roots and predisposing them to fungal pathogens.",
            "treatments": [
                {
                    "name": "Substrate Drying & Aeration Intervention",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Insert wooden chopstick into soil to aerate root zone. Cease watering until top 3 inches feel bone dry. Move to brighter light.",
                    "product_id": None
                },
                {
                    "name": "Bio-Enzymatic Root Reviver Inoculation",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Mix 10ml of Bio-Enzymatic Drench per liter of water when soil dries slightly to colonize root zone with beneficial fungi.",
                    "product_id": root_prod.id
                },
                {
                    "name": "Perlite Pot Repotting",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Depot the plant, gently brush away soggy anaerobic soil, and repot into chunky potting mix containing 30% coarse perlite.",
                    "product_id": None
                }
            ]
        },
        {
            "plant_part": "stem",
            "observation": "Sticky white cotton-like fluff clustering in stem joints",
            "diagnosis": "Mealybug Infestation (Pseudococcidae)",
            "cause": "Soft-bodied scale insects secreting protective waxy filaments while feeding on stem vascular phloem.",
            "treatments": [
                {
                    "name": "Direct Isopropyl Alcohol Spot Treatment",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Dip a cotton swab in 70% rubbing alcohol and press directly onto visible white clusters to dissolve their protective wax shell.",
                    "product_id": None
                },
                {
                    "name": "Insecticidal Soap Stem Drench",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Spray stem junctions and leaf axils thoroughly until runoff. Apply twice weekly for 3 consecutive weeks.",
                    "product_id": soap_prod.id
                },
                {
                    "name": "Neem Oil Horticultural Coating",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Apply cold-pressed neem mixture to coat the stems and prevent juvenile crawlers from establishing new colonies.",
                    "product_id": neem_prod.id
                },
                {
                    "name": "Systemic Chemical Pesticide Granules",
                    "treatment_type": "chemical",
                    "pet_safe": False,
                    "child_safe": False,
                    "edible_safe": False,
                    "instructions": "Work chemical systemic granules into top inch of soil. Absorbed by roots into plant sap. Toxic if ingested by domestic pets.",
                    "product_id": None
                }
            ]
        },
        {
            "plant_part": "stem",
            "observation": "Dark brown sunken water-soaked soft lesions on stem",
            "diagnosis": "Bacterial Stem Rot / Canker (Dickeya / Erwinia)",
            "cause": "Bacterial pathogens penetrating stem wounds or micro-tears during high humidity and unsterilized pruning.",
            "treatments": [
                {
                    "name": "Surgical Stem Debridement & Cinnamon Dusting",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Sterilize blade in flame or alcohol. Excise dark mushy tissue into clean green wood. Dust freshly cut wound with natural cinnamon powder.",
                    "product_id": None
                },
                {
                    "name": "Potassium Bicarbonate Bio-Barrier",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Mix into a paste with minimal water and dab directly around excision margins to halt bacterial spread.",
                    "product_id": fungicide_bio.id
                },
                {
                    "name": "Copper Hydroxide Wound Sealant",
                    "treatment_type": "chemical",
                    "pet_safe": False,
                    "child_safe": False,
                    "edible_safe": False,
                    "instructions": "Paint concentrated liquid copper onto affected stem area. Wear protective rubber gloves.",
                    "product_id": copper_prod.id
                }
            ]
        },
        {
            "plant_part": "root",
            "observation": "Black, squishy mushy roots emitting a sour sulfur odor",
            "diagnosis": "Advanced Fungal Root Rot (Pythium / Phytophthora)",
            "cause": "Prolonged standing water and lack of oxygen causing root necrosis and opportunistic fungal colonization.",
            "treatments": [
                {
                    "name": "Emergency Root Surgery & Peroxide Wash",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Wash all soil from roots under running water. Cut away all mushy brown/black roots with sterile shears until only firm white root remains.",
                    "product_id": None
                },
                {
                    "name": "Bio-Enzymatic Trichoderma Root Drench",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Soak surviving bare roots in Bio-Enzymatic root reviver solution for 20 minutes before repotting into fresh sterile medium.",
                    "product_id": root_prod.id
                },
                {
                    "name": "Chemical Anti-Pythium Fungicide Soak",
                    "treatment_type": "chemical",
                    "pet_safe": False,
                    "child_safe": False,
                    "edible_safe": False,
                    "instructions": "Drench root ball with chemical systemic fungicide prior to repotting. Strictly isolate from domestic animals.",
                    "product_id": copper_prod.id
                }
            ]
        },
        {
            "plant_part": "root",
            "observation": "Dense spiral roots wrapping around pot base; water drains instantly",
            "diagnosis": "Severe Pot-Bound Root Restriction",
            "cause": "Root mass has completely occupied container volume and exhausted organic mineral potting medium.",
            "treatments": [
                {
                    "name": "Root Teasing and Pot Up-sizing",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Gently massage the lower outer root ring to loosen circling roots. Repot into a container 2 inches larger in diameter.",
                    "product_id": None
                },
                {
                    "name": "Horizontal Root Pruning for Same-Pot Maintenance",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Slice off bottom 20% of the thick root mat with a clean saw or knife. Backfill original container with fresh nutrient-rich compost.",
                    "product_id": None
                },
                {
                    "name": "Mycorrhizal Bio-Inoculation Drench",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Water newly repotted root structure with Bio-Enzymatic root inoculant to encourage rapid lateral feeder root development.",
                    "product_id": root_prod.id
                }
            ]
        },
        {
            "plant_part": "flower",
            "observation": "Flower buds dry up, turn yellow-brown, and drop before opening",
            "diagnosis": "Flower Bud Blast & Abscission",
            "cause": "Sudden temperature fluctuations, dry ambient air drafts, or exposure to ethylene gas from nearby ripening fruit.",
            "treatments": [
                {
                    "name": "Microclimate Stabilization",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Move plant to a draft-free location maintaining steady 18-24°C temperature. Keep away from air conditioning vents and fruit bowls.",
                    "product_id": None
                },
                {
                    "name": "Organic Bottom-Watering & Humidification",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Water consistently from bottom tray using lukewarm rainwater or dechlorinated tap water to prevent bud shock.",
                    "product_id": None
                },
                {
                    "name": "Neem Oil Flower Spathe Guard",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Mist outer bud calyx with mild neem oil in early morning to deter microscopic bud thrips.",
                    "product_id": neem_prod.id
                }
            ]
        },
        {
            "plant_part": "flower",
            "observation": "Silvery streaks on petals with dark specks and chewed margins",
            "diagnosis": "Flower Thrips Infestation (Frankliniella occidentalis)",
            "cause": "Minute slender fringed-wing thrips invading flower blossoms to puncture plant cells and consume nectar and sap.",
            "treatments": [
                {
                    "name": "Organic Insecticidal Soap Flower Rinse",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Spray opened petals lightly at dusk with Insecticidal Soap to suffocate adult thrips without scorching petals in sun.",
                    "product_id": soap_prod.id
                },
                {
                    "name": "Cold-Pressed Neem Oil Blossom Treatment",
                    "treatment_type": "organic",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Apply diluted neem oil mixture at the base of flower stems and petals weekly.",
                    "product_id": neem_prod.id
                },
                {
                    "name": "Blue Sticky Trap Canopy Installation",
                    "treatment_type": "non-chemical",
                    "pet_safe": True,
                    "child_safe": True,
                    "edible_safe": True,
                    "instructions": "Hang blue sticky cards right above the flower canopy. Thrips are strongly attracted to specific blue wavelengths.",
                    "product_id": None
                },
                {
                    "name": "Spinosad Chemical Insecticide",
                    "treatment_type": "chemical",
                    "pet_safe": False,
                    "child_safe": False,
                    "edible_safe": False,
                    "instructions": "Targeted chemical treatment for heavy commercial infestations. Do not spray outdoors when bees are actively foraging.",
                    "product_id": None
                }
            ]
        }
    ]

    for symp_data in symptoms_data:
        treatments_list = symp_data.pop("treatments")
        symptom = Symptom(**symp_data)
        db.add(symptom)
        db.flush()
        for t_data in treatments_list:
            treatment = Treatment(symptom_id=symptom.id, **t_data)
            db.add(treatment)
    db.flush()

    # 5. Import Rules (SAMPLE DATA)
    # Countries: Nepal, India, United States, United Kingdom, Australia
    import_rules_data = [
        # --- Nepal ---
        {
            "country": "Nepal",
            "plant_name": "*",
            "required_documents": "Plant Import Permit (issued by PQPMC Nepal)\nOfficial Phytosanitary Certificate from exporting country NPPO\nCommercial Invoice & Airway Bill / Bill of Lading\nCustoms Declaration Form (TIA or dry port border checkpost)",
            "is_banned": False,
            "cites_protected": False,
            "notes": "General clearance required at Plant Quarantine and Pesticide Management Centre (PQPMC), Hariharbhawan / TIA Customs."
        },
        {
            "country": "Nepal",
            "plant_name": "orchid",
            "required_documents": "CITES Export Permit from country of origin\nCITES Import Endorsement from Department of Forests and Soil Conservation, Nepal\nPhytosanitary Certificate stating wild or artificially propagated status",
            "is_banned": False,
            "cites_protected": True,
            "notes": "All Orchidaceae family species fall under CITES Appendix I or II regulations in Nepal."
        },
        {
            "country": "Nepal",
            "plant_name": "paphiopedilum",
            "required_documents": "CITES Appendix I Import and Export Permits\nScientific verification certificate of artificial propagation\nPQPMC Special Import Permit",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Paphiopedilum (Asian Slipper Orchids) are strictly protected under CITES Appendix I. Commercial wild trade is strictly prohibited."
        },
        {
            "country": "Nepal",
            "plant_name": "cycad",
            "required_documents": "CITES Appendix II Permit\nNPPO Phytosanitary Certificate\nSoil-free root verification certificate",
            "is_banned": False,
            "cites_protected": True,
            "notes": "All Cycadales species require international CITES documentation before crossing customs."
        },
        {
            "country": "Nepal",
            "plant_name": "cactus",
            "required_documents": "CITES Appendix II Permit\nPhytosanitary Certificate\nPQPMC Clearance",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Cactaceae family specimens require CITES documentation (except certified flasked micro-propagated seedlings)."
        },
        # --- India ---
        {
            "country": "India",
            "plant_name": "*",
            "required_documents": "Import Permit issued under Plant Quarantine Order 2003 via DPPQS\nPhytosanitary Certificate from exporting NPPO\nSoil-free growing media certification\nBill of Lading and Certificate of Origin",
            "is_banned": False,
            "cites_protected": False,
            "notes": "Cleared through National Plant Quarantine Station (e.g. New Delhi, Mumbai, Kolkata, Chennai)."
        },
        {
            "country": "India",
            "plant_name": "orchid",
            "required_documents": "CITES Export Permit\nWildlife Crime Control Bureau (WCCB) India NOC\nPhytosanitary Certificate\nPQ Permit with pest risk assessment endorsement",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Orchid imports strictly regulated by Wildlife Crime Control Bureau (WCCB) and DPPQS."
        },
        {
            "country": "India",
            "plant_name": "paphiopedilum",
            "required_documents": "CITES Appendix I Import Permit issued by MoEFCC India\nCITES Export Permit from source country\nDPPQS Quarantine License",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Appendix I specimen. Only permitted for recognized scientific institutions or verified tissue-culture propagations."
        },
        {
            "country": "India",
            "plant_name": "cycad",
            "required_documents": "CITES Appendix II Certificate\nWCCB Clearance\nPhytosanitary Certificate",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Strict phytosanitary inspection for Cycad Aulacaspis scale."
        },
        {
            "country": "India",
            "plant_name": "cactus",
            "required_documents": "CITES Appendix II Documentation\nDPPQS Import Permit\nPhytosanitary Certificate",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Living cacti require soil-free roots and verified nursery propagation certificate."
        },
        # --- United States ---
        {
            "country": "United States",
            "plant_name": "*",
            "required_documents": "USDA APHIS Form PPQ 587 (Permit to Import Plants or Plant Products)\nForeign Phytosanitary Certificate issued within 14 days of shipment\nUSDA CBP Declaration Form 7501\nDesignated Plant Inspection Station (PIS) Routing Label",
            "is_banned": False,
            "cites_protected": False,
            "notes": "Regulated under USDA Animal and Plant Health Inspection Service (APHIS) 7 CFR 319.37."
        },
        {
            "country": "United States",
            "plant_name": "orchid",
            "required_documents": "CITES Export Permit / Re-export Certificate\nUSDA APHIS PPQ 587 Permit\nPhytosanitary Certificate with nursery propagation declaration",
            "is_banned": False,
            "cites_protected": True,
            "notes": "CITES Appendix II. Must clear through designated USDA APHIS Plant Inspection Station (e.g. Miami, JFK, LAX)."
        },
        {
            "country": "United States",
            "plant_name": "paphiopedilum",
            "required_documents": "USFWS CITES Appendix I Import Permit (Form 3-200-37)\nForeign CITES Appendix I Export Permit\nUSDA APHIS PPQ 587 Permit",
            "is_banned": False,
            "cites_protected": True,
            "notes": "US Fish and Wildlife Service (USFWS) co-enforcement. Prohibited from commercial wild harvest."
        },
        {
            "country": "United States",
            "plant_name": "cycad",
            "required_documents": "CITES Export Permit\nUSFWS Declaration Form 3-177\nUSDA APHIS Import Permit",
            "is_banned": False,
            "cites_protected": True,
            "notes": "CITES protected. Soil substrate strictly prohibited; roots must be washed clean and packed in sterile peat or sphagnum."
        },
        {
            "country": "United States",
            "plant_name": "cactus",
            "required_documents": "CITES Export Documentation\nUSDA APHIS Permit\nPhytosanitary Certificate",
            "is_banned": False,
            "cites_protected": True,
            "notes": "All Cactaceae regulated under CITES Appendix II (some Ariocarpus, Discocactus in App I)."
        },
        {
            "country": "United States",
            "plant_name": "water hyacinth",
            "required_documents": "IMPORT STRICTLY PROHIBITED",
            "is_banned": True,
            "cites_protected": False,
            "notes": "Eichhornia crassipes is a designated Federal Noxious Weed under 7 CFR 360. Importation, transport, and interstate movement are prohibited by federal law."
        },
        # --- United Kingdom ---
        {
            "country": "United Kingdom",
            "plant_name": "*",
            "required_documents": "IPAFFS Import Notification (DEFRA / APHA)\nOfficial Phytosanitary Certificate from exporting country\nCustoms declaration (HMRC CDS)\nUK Border Control Post (BCP) Document Check",
            "is_banned": False,
            "cites_protected": False,
            "notes": "Governed by Plant Health Regulation (Retained EU Law) 2016/2031 through DEFRA / APHA."
        },
        {
            "country": "United Kingdom",
            "plant_name": "orchid",
            "required_documents": "UK CITES Import Permit (issued by APHA Bristol)\nValid CITES Export Permit from exporting country\nPhytosanitary Certificate uploaded to IPAFFS",
            "is_banned": False,
            "cites_protected": True,
            "notes": "UK Border Force verifies CITES permits at designated CITES points of entry."
        },
        {
            "country": "United Kingdom",
            "plant_name": "paphiopedilum",
            "required_documents": "UK CITES Appendix I Import Permit\nCountry of Export Appendix I Export Permit\nIPAFFS Priority Notification",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Strictly regulated endangered species under UK Endangered Species (Import and Export) Act."
        },
        {
            "country": "United Kingdom",
            "plant_name": "cycad",
            "required_documents": "UK CITES Import Permit\nExporting Country CITES Document\nDEFRA Phytosanitary Clearance",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Appendix II listed. Controlled entry through London Heathrow or approved BCPs."
        },
        {
            "country": "United Kingdom",
            "plant_name": "cactus",
            "required_documents": "UK CITES Documentation\nPhytosanitary Certificate\nIPAFFS Import Notification",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Applies to all live cactus species and grafting stock."
        },
        # --- Australia ---
        {
            "country": "Australia",
            "plant_name": "*",
            "required_documents": "DAFF Import Permit (applied through BICON system)\nForeign NPPO Phytosanitary Certificate\nPost-Entry Quarantine (PEQ) Booking Confirmation (Mickleham, Victoria)\nDeclaration of Treatment (e.g. Methyl Bromide or approved pesticide dip)",
            "is_banned": False,
            "cites_protected": False,
            "notes": "Australia enforces the world's strictest biosecurity controls under the Biosecurity Act 2015. Most live plants require mandatory 3-month PEQ growth."
        },
        {
            "country": "Australia",
            "plant_name": "orchid",
            "required_documents": "Australian CITES Import Permit (Department of Climate Change, Energy, the Environment and Water - DCCEEW)\nExporting Country CITES Permit\nDAFF BICON Import Permit\nPEQ Quarantine Reservation",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Live orchids require pre-booked quarantine housing at the government Post Entry Quarantine facility."
        },
        {
            "country": "Australia",
            "plant_name": "paphiopedilum",
            "required_documents": "DCCEEW CITES Appendix I Permit\nOverseas CITES Appendix I Export Authority\nDAFF Import Permit\nMickleham PEQ Growth Clearance",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Only artificially propagated specimens from verified registered nurseries will be considered by DCCEEW."
        },
        {
            "country": "Australia",
            "plant_name": "cycad",
            "required_documents": "Australian CITES Permit\nDAFF Plant Import Permit\nOfficial Treatment & Bare-Root Certificate",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Must be free from all soil and plant debris; fumigation at port of departure required."
        },
        {
            "country": "Australia",
            "plant_name": "cactus",
            "required_documents": "DAFF BICON Live Cactus Permit\nCITES Certificate\nPEQ Inspection Booking",
            "is_banned": False,
            "cites_protected": True,
            "notes": "Strictly examined for mealybugs, scales, and fungal pathogens."
        },
        {
            "country": "Australia",
            "plant_name": "water hyacinth",
            "required_documents": "ENTRY STRICTLY PROHIBITED - PROHIBITED WEED",
            "is_banned": True,
            "cites_protected": False,
            "notes": "Eichhornia crassipes is a Weed of National Significance (WoNS) and Tier 1 Prohibited Matter in Australia. Unlawful import results in severe legal penalties under the Biosecurity Act 2015."
        }
    ]

    for rule_data in import_rules_data:
        rule = ImportRule(**rule_data)
        db.add(rule)
    db.flush()

    # 6. Sample Wanted Request & Offer
    wanted_req = WantedRequest(
        buyer_id=buyer_user.id,
        plant_name="Variegated Monstera Deliciosa (Large Form)",
        destination_country="Nepal",
        details="Seeking an established rooted top-cutting of large form Thai Constellation or Albo with high sectoral variegation. Must have healthy aerial roots.",
        status="open"
    )
    db.add(wanted_req)
    db.flush()

    sample_offer = Offer(
        request_id=wanted_req.id,
        seller_id=seller_user.id,
        price=16500.0,
        message="I have a 3-leaf rooted cutting with verified high sectoral variegation in a 6-inch nursery pot. Happy to provide phytosanitary certification.",
        status="pending"
    )
    db.add(sample_offer)

    db.commit()


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
        print("Database successfully seeded.")
    finally:
        db.close()

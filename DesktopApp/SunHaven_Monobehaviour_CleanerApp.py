# import required module
import os
import shutil
import logging

def isRecipe(f):
    return 'Recipe ' in f
def isTool(f):
    return f.startswith('Axe') or \
            f.startswith('Pickaxe') or \
            f.startswith('Hoe') or \
            f.startswith('Sword') or \
            f.startswith('WateringCan') or \
            f.startswith('CrossBow') or \
            f.startswith('FishingRod')
def isRecipeList(f):
    return f.startswith('RecipeList')
def isWhistle(f):
    return 'Whistle' in f
def isRecord(f):
    return 'Record' in f
def isMerchant(f):
    return ('MerchantTable.json' in f)
def isNPC(f):
    return ('WalkCycle' in f) or \
        f.endswith('WalkPath.json') or \
        ('PathA' in f) or \
        ('PathB' in f) or \
        ('PathRain' in f)
def isCutscene(f):
    return ('Cutscene' in f)
def isWaterEdgeTile(f):
    return ('water_edge_tiles' in f) or f.startswith('Side_of_Water_Tiles')
def isSceneSetting(f):
    return ('SceneSettings' in f)
def isQuest(f):
    return ('Quest.json' in f)
def isMail(f):
    return ('Mail' in f)
def isGiftTable(f):
    return ('GiftTable.json' in f)
def isRecurringChest(f):
    return f.startswith('RecurringChest')
def isDebugUIHandler(f):
    return f.startswith('DebugUIHandler')
def isPerk(f):
    return (f.startswith('Combat') and f[6].isnumeric()) or \
        (f.startswith('Exploration') and f[11].isnumeric()) or \
        (f.startswith('Farming') and f[7].isnumeric()) or \
        (f.startswith('Fishing') and f[7].isnumeric()) or \
        (f.startswith('Mining') and f[6].isnumeric())
def isSkillLevelReward(f):
    return (f.startswith('CombatLevel') and f[11].isnumeric()) or \
        (f.startswith('ExplorationLevel') and f[16].isnumeric()) or \
        (f.startswith('FarmingLevel') and f[12].isnumeric()) or \
        (f.startswith('FishingLevel') and f[12].isnumeric()) or \
        (f.startswith('MiningLevel') and f[11].isnumeric())
def isHardware(f):
    return f.startswith('3D') or \
        f.startswith('8Bitdo') or \
        f.startswith('Buffalo') or \
        f.startswith('CHFighter') or \
        f.startswith('CHPro') or \
        f.startswith('CHThrottle') or \
        f.startswith('Logitech') or \
        f.startswith('Microsoft') or \
        f.startswith('Nintendo') or \
        f.startswith('OpenVR') or \
        f.startswith('Saitek') or \
        f.startswith('Samsung') or \
        f.startswith('Sony') or \
        f.startswith('Thrustmaster') or \
        f.startswith('ThrustMaster') or \
        f.startswith('XiaoMi') or \
        f.startswith('XInput') or \
        f.startswith('Zhidong')
def isGoldenPom(f):
    return f.startswith('GoldenPom')
def isMuseum(f):
    return f.startswith('MuseumAquarium') or \
        ('AlchemyBundle' in f) or \
        ('CropsBundle' in f) or \
        ('ExplorationBundle' in f) or \
        ('FarmingBundle' in f) or \
        ('FishingBundle' in f) or \
        ('ForagingBundle' in f) or \
        ('GemBundle' in f) or \
        ('ManaBundle' in f) or \
        ('MinesBundle' in f) or \
        ('MoneyBundle' in f)

def isWithergateTile(f):
    return f.startswith('Withergate_cliff_tiles') or \
           f.startswith('withergate_tiles') or \
           f.startswith('Withergate_tiles') or \
           f.startswith('WithergateRoadTiles') or \
           f.startswith('withergatefarm_tiles') or \
           f.startswith('wg_rooftop_farm_dirtbase') or \
           f.startswith('Dynus_dirtroad_tiles') or \
           f.startswith('Sewer_clifs') or \
           f.startswith('Sewer_pier_tiles') or \
           f.startswith('Withergate_farming_roof_') or \
           f.startswith('Dragon_meet_tiles') or \
           f.startswith('throne_room_floor') or \
           f.startswith('WithergateThroneRoomBorderTiles')
def isNelvariTile(f):
    return f.startswith('elven_dirt_road_') or \
           f.startswith('Elventiles_') or \
           f.startswith('Nivara_Tiles') or \
           f.startswith('nelvarifarm_tiles') or \
           f.startswith('nelvari_jumpspot_tiles') or \
           f.startswith('purple_rooftiles') or \
           f.startswith('purple_tile_herb')
def isSunhavenTile(f):
    return f.startswith('beach_tiles') or \
           f.startswith('Beach_pier_tiles') or \
           f.startswith('barn_floor_tiles') or \
           f.startswith('farm_dirt') or \
           f.startswith('Farm_dirt') or \
           f.startswith('farm_tiles') or \
           f.startswith('Grass_Patches_') or \
           f.startswith('Ho_and_water_') or \
           f.startswith('HumanClifTiles_') or \
           f.startswith('Sunhaven_Tiles') or \
           f.startswith('SunhavenSidewalk') or \
           f.startswith('town_tile_edits') or \
           f.startswith('Woodcutting_Forest_Grass_Tiles') or \
           f.startswith('ceilingtilestest') or \
           f.startswith('Forest_tileset') or \
           f.startswith('Hexagon town center') or \
           f.startswith('SunHaven_Town_Center_') or \
           f.startswith('WornhardtTiles')
def isFloorTile(f):
    return f.startswith('floor_') or \
        f.startswith('Floortile_') or \
        f.startswith('grey_large_tile') or \
        f.startswith('Gum_tiles')

def isCharCustomization(f):
    for i in charCustomizationTags:
        if f.startswith(i):
            return True
    return False
def isClothes(f):
    for i in clothingTags:
        if f.startswith(i):
            return True
    return (f.startswith('chest') and f[5].isnumeric())
 
def isLargeDatatype(f, datatype):
    return f.startswith(datatype+' #') or (f == datatype+'.json')
def isItem(f):
    return f[0].isnumeric() and f[1].isnumeric() and f[2].isnumeric()

def isFile(f):
    return os.path.isfile(f)
def isFolder(f):
    return os.path.isdir(f)


largeDatatypes = ["BeeHiveBox", "Bobber", "ClothingColorButton", "ClothingImageButton", "CraftingNotificationBubble", "CurrencyDepositButton", \
                  "DataTile", "Entity", "FarmSellingCrate", "Fertilizer", "HighlightButton", "InstrumentInspectable", "MeshGenerator", \
                  "MusicZone", "Plant", "RendererShadows", "SeasonEntity", "Image", "NavigationElement", "Poacher", "TilePlaceable", "Tree",\
                  "Slot", "TextMeshProUGUI", "TMP_SubMeshUI", "TMP_Dropdown", "TMP_InputField", "Button", "ClifMaker", "LightFlicker", "Water", \
                  "VerticalLayoutGroup", "UniversalAdditionalCameraData", "StartIdleRandomly", "Slider", "RandomSprite", "AdaptiveUIScale", \
                  "AggroRange", "AIAnimationTester", "AmbientLightZone", "AnimalCanvas", "AnimalNamingCanvas", "BigTree", "BuyableItem", \
                  "CameraBounds", "Candle", "CanvasScaler", "Cart", "Chest", "CinematicCamera", "ContentSizeFitter", "Costume", "CraftingPanel", \
                  "CraftingTab", "CraftingTable", "CraftingUI", "Crop", "DamageSource", "Decoration", "DecorativeTree", "Deer", \
                  "DestructibleDecoration", "DOTweenAnimation", "EnableAtTime", "EnemyAI", "EnemyCanvas", "EnemySpawner", "EnemySpawnGroup", \
                  "EventSystem", "Fence", "FireFlies", "Fish", "FishSpawner", "FloatUpAndDown", "Forageable", "ForageTree", "Ghost", "Godray", \
                  "GraphicRaycaster", "Grid", "GridLayoutGroup", "HangoutCutscene", "HorizontalLayoutGroup", "HungryMonster", "Inspectable", \
                  "Inventory", "ItemRequirement", "JumpSpot", "JumpZone", "Keybind", "LayoutElement", "LiamWheat", "LightGlow", "MainMusic", \
                  "Mask", "MineGate", "MineGenerator2", "MineLock", "Monkey", "MountOffset", "MuseumPodium", "NetworkEnemy", "NetworkIdentity", \
                  "NetworkTransform", "NoiseLocalPosition", "NPCAI", "NPCQuestIcons", "OneTimeChest", "OnHover", "Pathfinding", "Placeable", \
                  "Platform", "Popup", "PostProcessLayer", "PostProcessVolume", "ProgressTrigger", "QuestDialogueOverride", "RainbowRoad", \
                  "RectMask2D", "RenderDepth", "Rock", "RotatableDecoration", "RotatablePlaceable", "ScenePortalSpot", "ScollingMaterial", \
                  "Scrollbar", "ScrollButtonController", "ScrollRect", "SeasonEventUI", "Seeds", "Shop", "ShopMoneyUI", "ShopUI", \
                  "StandaloneInputModule", "Table", "Text", "TextSizer", "TextureNPC", "TextureNPCAnimationSound", "Tile", "Toggle", \
                  "ToggleGroup", "Trampoline", "Wall", "Wood", "WorldTree", "Animal", "AnimalFoodFeeder", "AnimalSpawnItem", "AnimationHandler", \
                  "AnimationIndex", "AquariumBundleVisual", "Bed", "Book", "BossMiningShardAttack", "Bridge", "BridgeCustomizationKit", \
                  "CameraController", "CarnivalFoodMachine", "CloudsMoving", "CombatDungeon", "CommunityTokenMoneyUI", "ConsumableBag", \
                  "DebugUIHandlerIndirectFloatField", "DebugUIHandlerIndirectToggle", "DoorKnockController", "EventTrigger", "ExaminableRewards", \
                  "FishingPermit", "FoodStats", "ForageTreePlaceable", "GhostBook", "GoldenPomegranatePickup", "HealthDecoration", \
                  "LanternFestLantern", "LocationName", "Lynn", "MagazineInspectable", "MonoBehaviour", "MountWhistle", "MuseumBundleVisual", \
                  "NPCMount", "NPCSpawnManager", "Pet", "PetSpawnItem", "PlayerMount", "PlayerStats", "PopOnHover", "ProgressEnable", \
                  "Projectile", "RepairableBuilding", "RepairSign", "SaleStand", "Scarecrow", "SeasonsManager", "SetInteractiveShaderEffects", \
                  "SkillTreeColumn", "TargetDummy", "WindTunnel", "ItemImage", "MapImage", "ScrollButton", "SkillPotion", "UIButton", "FishingNet", \
                  "TreeDamageable", "TreePlaceable", "ActionBarIcon", "AmbientSound", "Bee", "BlockedZoneTrigger", "BossCraftingSpawnBlobs", \
                  "CameraDrone", "CameraZone", "CarnivalShopMoneyUI", "CatenaryLineRenderer", "CombatDungeonChest", "ConsumableStat", \
                  "CustomCurrencyMoneyUI", "FerrisWheelSeats", "FireSpell", "HouseRomanceRooms", "JBBean", "LerpPositionToTransform", \
                  "MainMusicVariation", "ManaInfuser", "MGCard", "PickupDecoration", "PlaceableZoomOut", "QuestPickup", "QuestPlaceable", \
                  "QuestWood", "SavePanel", "Sign", "SubwayTrain", "TaskPostit", "UIFoldout"]

clothingTags = ['angelic_dress', 'BaseballHat_', 'beltedpants_', 'BoneArmor', 'bowtie_shirt_', 'bunny_ears_', 'butterfly_elf_wing_', 'cape_', 'cape1_', 'cape2_', \
                'caped1_', 'chefhat_', 'chest_', 'Chest_', 'cool_vest_', 'cowboy_hat_', 'dress_', 'fairywings_', 'fall_armor_', 'generic_pants', 'gloves_', 'glowing_sun_', 'gold_chefhat', 'gold_feather', 'hat_', \
                'hats_', 'helmet_', 'icecream_hat', 'large_hat_', 'legionnaire_armor', 'legionnaire_sun_armor', 'letterman_jacket', 'magmaOutfit_', 'pants_', \
                'pants_vampire', 'pastel_skirt', 'schoolboy_shirt', 'shoeswithpants', 'shirt_', 'skirt_', 'skirt2_', 'skirtlegs2_', 'spring_armor_', 'street_pants_', \
                'stripe_thin_shirt', 'stripe_thick_shirt', 'tophat_', 'torn_dress', 'wig_', 'winter_armor_', 'witch_hat', 'back_', 'cool_pants_', \
                'angel_wing_dress', 'anchor_shirt', 'goldOutfit_', 'magic_circlet', 'MiningArmor', 'Mining Hat', 'MiningAccessories', 'scratch_chest_' ]

charCustomizationTags = ['AmariCat_', 'amari_bird_chest', 'amari_cat_chest', 'amari_dog_chest', 'AmariBird_', 'Amari_Lizard_', 'angel_hairStyle_', \
                        'Angel_hairStyle_', 'Angel_wings_', 'angel_halo1_', 'Angel_halo1_', 'AngelCustomization_', 'beard', 'body_', 'buzzhair_', \
                        'cat_dress', 'cat_hair', 'cat_tail', 'cat_whiskers', 'Demon_custom_fix_', 'Demon_horns_', 'demon_wings_', 'Demons_hairStyle_', \
                        'DogAmari_', 'ears_', 'Elf_custom_', 'elfhorns_', 'elfmask_', 'eyes_', 'face_amari_', 'face_none', 'Fix_Water_hair_', 'hair_', \
                        'Hair_', 'halo3_', 'horns_amari_', 'horns_demon_', 'mask_elf', 'naga_', 'nagas_fix_', 'tail_', 'wing_bird_', 'wings_', \
                        'silver_feather_', 'slash_chest_', 'warcaster', 'wrap_dress']

def Clean(srcFolder, dstFolder):

    # iterate over files
    for filename in os.listdir(srcFolder):
        srcFilepath = os.path.join(srcFolder, filename)
        # checking if it is a file
        if isFile(srcFilepath):

            # Move Mega Files
            for datatype in largeDatatypes:
                if isLargeDatatype(filename, datatype):
                    foldername = datatype
                    break
            else:
                # And Wanted Files
                if isItem(filename):
                    foldername = "Item"
                elif isMerchant(filename):
                    foldername = "MerchantTable"
                elif isRecipe(filename):
                    foldername = "Recipe"
                elif isRecipeList(filename):
                    foldername = "RecipeList"
                elif isCharCustomization(filename):
                    foldername = "CharCustomization"
                elif isNPC(filename):
                    foldername = "Npc"
                elif isCutscene(filename):
                    foldername = "Cutscene"
                elif isWaterEdgeTile(filename):
                    foldername = "WaterEdgeTile"
                elif isSunhavenTile(filename):
                    foldername = "SunhavenTile"
                elif isNelvariTile(filename):
                    foldername = "NelvariTile"
                elif isWithergateTile(filename):
                    foldername = "WithergateTile"
                elif isSceneSetting(filename):
                    foldername = "SceneSetting"
                elif isQuest(filename):
                    foldername = "Quest"
                elif isMail(filename):
                    foldername = "Mail"
                elif isClothes(filename):
                    foldername = "Clothes"
                elif isGiftTable(filename):
                    foldername = "GiftTable"
                elif isTool(filename):
                    foldername = "Tool"
                elif isRecurringChest(filename):
                    foldername = "RecurringChest"
                elif isDebugUIHandler(filename):
                    foldername = "RecurringChest"
                elif isPerk(filename):
                    foldername = "Perk"
                elif isFloorTile(filename):
                    foldername = "FloorTile"
                elif isHardware(filename):
                    foldername = "Controller"
                elif isSkillLevelReward(filename):
                    foldername = "SkillLevelReward"
                elif isGoldenPom(filename):
                    foldername = "GoldenPom"
                elif isMuseum(filename):
                    foldername = "MuseumBundle"
                else:
                    continue
            
            dstFolderpath = os.path.join(dstFolder, foldername)

            # If the folder does not exist, add it
            if not isFolder(dstFolderpath):
                logging.debug("Making "+foldername)
                os.mkdir(dstFolderpath)

            # Move the file
            shutil.move(srcFilepath, dstFolderpath)

"""Toolkit 0.5.1.18 class/member definitions and inert default values.

Authoring reference: read-only installed MyAssets, 2026-11-01. No native files,
image bytes, scene geometry, source notes or saved fog are shipped here. Byte
arrays are generated PNG parameters; positions/names/paths are assigned by code.
BinaryType/PrimitiveType values follow the existing bounded NRBF writer.
"""

LIBRARIES = {2: 'Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null'}

CLASSES = {
    'ArkenMapTileUpgradeBase': {
        'name': 'ArkenMapTileUpgradeBase',
        'names': [
            '_tileInfo',
            '_placementType',
            '_brushType',
            '_gridType',
            'spriteWidth',
            'spriteRatio',
            '_trueSize',
            '_additionalData'
        ],
        'types': [4, 4, 4, 4, 0, 0, 0, 3],
        'infos': [
            {'name': 'ArkenTilePresetBase', 'library_id': 2},
            {'name': 'MapOptions+ObjectPlacementType', 'library_id': 2},
            {'name': 'MapOptions+PlacementType', 'library_id': 2},
            {'name': 'MapOptions+GridType', 'library_id': 2},
            11,
            11,
            11,
            'System.Collections.Generic.List`1[[System.Object, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]'
        ],
        'library_id': 2
    },
    'ArkenTilePresetRepeatable': {
        'name': 'ArkenTilePresetRepeatable',
        'names': [
            '_points',
            '_width',
            '_worldSpaceTexture',
            '_tileScale',
            '_startTaper',
            '_endTaper',
            '_scrollPos',
            '_fadeLine',
            '_fadeLineFlipDirection',
            '_fadeStartPoint',
            '_loop',
            '_name',
            '_editable',
            '_visibleInLibrary',
            '_official',
            '_imported',
            '_version',
            '_tileName',
            '_tilePack',
            '_tileCreator',
            '_tilePath',
            '_tileType',
            '_category',
            '_defaultPlacementType',
            '_position',
            '_pivot',
            '_rotation',
            '_scale',
            '_groupID',
            '_sortingOrder',
            '_mapLevel',
            '_onTerrainLayer',
            '_hidden',
            '_locked',
            '_superLocked',
            '_hue',
            '_brightness',
            '_saturation',
            '_opacity',
            '_tint',
            '_flipH',
            '_flipV',
            '_ignoreTimeOfDay',
            '_chromaKeyEnabled',
            '_chromaKeyColour',
            '_chromeKeyTolerance',
            '_lighting',
            '_hasDropShadow',
            '_blocksLight',
            '_animation',
            '_effectsNew',
            '_alphaFriendlyCollider',
            '_blocking',
            '_chromaKeyReplacementColour',
            '_chromaKeyReplacementAlpha',
            '_uID',
            '_blockedByMovementBlockers',
            'ArkenTilePresetBase+_name',
            'ArkenTilePresetBase+_baseName',
            'ArkenTilePresetBase+_editable',
            'ArkenTilePresetBase+_visibleInLibrary',
            'ArkenTilePresetBase+_official',
            'ArkenTilePresetBase+_imported',
            'ArkenTilePresetBase+_version',
            'ArkenTilePresetBase+_tileName',
            'ArkenTilePresetBase+_tilePack',
            'ArkenTilePresetBase+_tileCreator',
            'ArkenTilePresetBase+_tilePath',
            'ArkenTilePresetBase+_tileType',
            'ArkenTilePresetBase+_category',
            'ArkenTilePresetBase+_defaultPlacementType',
            'ArkenTilePresetBase+_position',
            'ArkenTilePresetBase+_pivot',
            'ArkenTilePresetBase+_rotation',
            'ArkenTilePresetBase+_scale',
            'ArkenTilePresetBase+_groupID',
            'ArkenTilePresetBase+_sortingOrder',
            'ArkenTilePresetBase+_mapLevel',
            'ArkenTilePresetBase+_onTerrainLayer',
            'ArkenTilePresetBase+_hidden',
            'ArkenTilePresetBase+_locked',
            'ArkenTilePresetBase+_superLocked',
            'ArkenTilePresetBase+_hue',
            'ArkenTilePresetBase+_brightness',
            'ArkenTilePresetBase+_saturation',
            'ArkenTilePresetBase+_opacity',
            'ArkenTilePresetBase+_tint',
            'ArkenTilePresetBase+_flipH',
            'ArkenTilePresetBase+_flipV',
            'ArkenTilePresetBase+_ignoreTimeOfDay',
            'ArkenTilePresetBase+_chromaKeyEnabled',
            'ArkenTilePresetBase+_chromaKeyColour',
            'ArkenTilePresetBase+_chromeKeyTolerance',
            'ArkenTilePresetBase+_lighting',
            'ArkenTilePresetBase+_hasDropShadow',
            'ArkenTilePresetBase+_blocksLight',
            'ArkenTilePresetBase+_animation',
            'ArkenTilePresetBase+_effects',
            'ArkenTilePresetBase+_effectsNew',
            'ArkenTilePresetBase+_alphaFriendlyCollider',
            'ArkenTilePresetBase+_blocking',
            'ArkenTilePresetBase+_chromaKeyReplacementColour',
            'ArkenTilePresetBase+_chromaKeyReplacementAlpha',
            'ArkenTilePresetBase+_uID',
            'ArkenTilePresetBase+_blockedByMovementBlockers',
            'ArkenTilePresetBase+_dropShadow',
            'ArkenTilePresetBase+_dropShadowLegacyUpgrade',
            'ArkenTilePresetBase+_ambience'
        ],
        'types': [
            3,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            4,
            4,
            4,
            4,
            4,
            0,
            4,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            4,
            0,
            0,
            0,
            0,
            4,
            0,
            4,
            0,
            0,
            4,
            3,
            0,
            4,
            4,
            0,
            0,
            0,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            4,
            4,
            4,
            4,
            4,
            0,
            4,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            4,
            0,
            0,
            0,
            0,
            4,
            0,
            4,
            0,
            0,
            4,
            3,
            3,
            0,
            4,
            4,
            0,
            0,
            0,
            4,
            0,
            4
        ],
        'infos': [
            'System.Collections.Generic.List`1[[SVector2, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            11,
            1,
            11,
            11,
            11,
            11,
            1,
            1,
            11,
            1,
            None,
            1,
            1,
            1,
            1,
            8,
            None,
            None,
            None,
            None,
            {'name': 'ArkenTile+TileType', 'library_id': 2},
            {'name': 'ArkenTileUpgrade+TileCategory', 'library_id': 2},
            {'name': 'MapOptions+ObjectPlacementType', 'library_id': 2},
            {'name': 'SVector2', 'library_id': 2},
            {'name': 'SVector2', 'library_id': 2},
            11,
            {'name': 'SVector2', 'library_id': 2},
            8,
            8,
            8,
            1,
            1,
            1,
            1,
            11,
            11,
            11,
            11,
            {'name': 'SVector3', 'library_id': 2},
            1,
            1,
            1,
            1,
            {'name': 'SVector3', 'library_id': 2},
            11,
            {'name': 'TileLightingProperties', 'library_id': 2},
            1,
            1,
            {'name': 'TileAnimationProperties', 'library_id': 2},
            'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            1,
            {'name': 'TileBlockingProperties', 'library_id': 2},
            {'name': 'SVector3', 'library_id': 2},
            11,
            9,
            1,
            None,
            None,
            1,
            1,
            1,
            1,
            8,
            None,
            None,
            None,
            None,
            {'name': 'ArkenTile+TileType', 'library_id': 2},
            {'name': 'ArkenTileUpgrade+TileCategory', 'library_id': 2},
            {'name': 'MapOptions+ObjectPlacementType', 'library_id': 2},
            {'name': 'SVector2', 'library_id': 2},
            {'name': 'SVector2', 'library_id': 2},
            11,
            {'name': 'SVector2', 'library_id': 2},
            8,
            8,
            8,
            1,
            1,
            1,
            1,
            11,
            11,
            11,
            11,
            {'name': 'SVector3', 'library_id': 2},
            1,
            1,
            1,
            1,
            {'name': 'SVector3', 'library_id': 2},
            11,
            {'name': 'TileLightingProperties', 'library_id': 2},
            1,
            1,
            {'name': 'TileAnimationProperties', 'library_id': 2},
            'System.Collections.Generic.List`1[[IObjectEffect, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            1,
            {'name': 'TileBlockingProperties', 'library_id': 2},
            {'name': 'SVector3', 'library_id': 2},
            11,
            9,
            1,
            {'name': 'TileDropShadowProperties', 'library_id': 2},
            1,
            {'name': 'TileAmbienceProperties', 'library_id': 2}
        ],
        'library_id': 2
    },
    'System.Collections.Generic.List`1[[SVector2, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]': {
        'name': 'System.Collections.Generic.List`1[[SVector2, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
        'names': ['_items', '_size', '_version'],
        'types': [4, 0, 0],
        'infos': [
            {'name': 'SVector2[]', 'library_id': 2},
            8,
            8
        ],
        'library_id': None
    },
    'SVector2': {
        'name': 'SVector2',
        'names': ['x', 'y'],
        'types': [0, 0],
        'infos': [11, 11],
        'library_id': 2
    },
    'ArkenTile+TileType': {
        'name': 'ArkenTile+TileType',
        'names': ['value__'],
        'types': [0],
        'infos': [8],
        'library_id': 2
    },
    'ArkenTileUpgrade+TileCategory': {
        'name': 'ArkenTileUpgrade+TileCategory',
        'names': ['value__'],
        'types': [0],
        'infos': [8],
        'library_id': 2
    },
    'MapOptions+ObjectPlacementType': {
        'name': 'MapOptions+ObjectPlacementType',
        'names': ['value__'],
        'types': [0],
        'infos': [8],
        'library_id': 2
    },
    'SVector3': {
        'name': 'SVector3',
        'names': ['x', 'y', 'z'],
        'types': [0, 0, 0],
        'infos': [11, 11, 11],
        'library_id': 2
    },
    'TileLightingProperties': {
        'name': 'TileLightingProperties',
        'names': [
            '_hasLight',
            '_lightRadius',
            '_lightR',
            '_lightG',
            '_lightB',
            '_visibleThroughFog',
            '_flicker',
            '_darkness',
            '_qualitySetting',
            '_fov',
            '_lightUpdates',
            '_lightIntensity',
            '_lightDirection'
        ],
        'types': [0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'infos': [
            1,
            'System.Collections.Generic.List`1[[System.Single, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            11,
            11,
            11,
            1,
            1,
            1,
            8,
            8,
            1,
            11,
            8
        ],
        'library_id': 2
    },
    'System.Collections.Generic.List`1[[System.Single, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]': {
        'name': 'System.Collections.Generic.List`1[[System.Single, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
        'names': ['_items', '_size', '_version'],
        'types': [7, 0, 0],
        'infos': [11, 8, 8],
        'library_id': None
    },
    'TileAnimationProperties': {
        'name': 'TileAnimationProperties',
        'names': [
            '_playing',
            '_currentFrame',
            '_framesPerSecond',
            '_noOfFrames',
            '_triggered',
            '_startFrame',
            '_endFrame',
            '_destroyAfterOnePlay',
            '_delay',
            '_delayTime',
            '_delayVariance',
            '_deactivateOnDelay',
            '_ghostTileFrame'
        ],
        'types': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'infos': [1, 8, 11, 11, 1, 11, 11, 1, 1, 11, 11, 1, 8],
        'library_id': 2
    },
    'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]': {
        'name': 'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
        'names': ['_items', '_size', '_version'],
        'types': [4, 0, 0],
        'infos': [
            {'name': 'ObjectEffectBase[]', 'library_id': 2},
            8,
            8
        ],
        'library_id': None
    },
    'TileBlockingProperties': {
        'name': 'TileBlockingProperties',
        'names': [
            '_blockingEnabled',
            '_light',
            '_vision',
            '_sound',
            '_movement',
            '_oneWay',
            '_oneWayDirection',
            '_toggleable',
            '_colliderMode'
        ],
        'types': [0, 0, 0, 0, 0, 0, 0, 0, 0],
        'infos': [1, 1, 1, 1, 1, 1, 1, 1, 8],
        'library_id': 2
    },
    'System.Collections.Generic.List`1[[IObjectEffect, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]': {
        'name': 'System.Collections.Generic.List`1[[IObjectEffect, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
        'names': ['_items', '_size', '_version'],
        'types': [4, 0, 0],
        'infos': [
            {'name': 'IObjectEffect[]', 'library_id': 2},
            8,
            8
        ],
        'library_id': None
    },
    'TileDropShadowProperties': {
        'name': 'TileDropShadowProperties',
        'names': [
            '_shadowActive',
            '_shadowStrengthUsesMapDefault',
            '_shadowStrength',
            '_shadowSizeUsesMapDefault',
            '_shadowSize',
            '_shadowDistanceUsesMapDefault',
            '_shadowDistance',
            '_shadowDirectionUsesMapDefault',
            '_shadowDirection',
            '_followsSunUsesMapDefault',
            '_dropShadowsFollowSun'
        ],
        'types': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'infos': [1, 1, 11, 1, 11, 1, 11, 1, 8, 1, 1],
        'library_id': 2
    },
    'TileAmbienceProperties': {
        'name': 'TileAmbienceProperties',
        'names': [
            '_active',
            '_audioPath',
            '_radius',
            '_falloffRadius',
            '_volume',
            '_playWhenHidden',
            '_activeTimeMin',
            '_activeTimeMax',
            '_playOnAllLevels'
        ],
        'types': [0, 1, 0, 0, 0, 0, 0, 0, 0],
        'infos': [1, None, 11, 11, 11, 1, 11, 11, 1],
        'library_id': 2
    },
    'MapOptions+PlacementType': {
        'name': 'MapOptions+PlacementType',
        'names': ['value__'],
        'types': [0],
        'infos': [8],
        'library_id': 2
    },
    'MapOptions+GridType': {
        'name': 'MapOptions+GridType',
        'names': ['value__'],
        'types': [0],
        'infos': [8],
        'library_id': 2
    },
    'ArkenTilePresetBase': {
        'name': 'ArkenTilePresetBase',
        'names': [
            '_name',
            '_baseName',
            '_editable',
            '_visibleInLibrary',
            '_official',
            '_imported',
            '_version',
            '_tileName',
            '_tilePack',
            '_tileCreator',
            '_tilePath',
            '_tileType',
            '_category',
            '_defaultPlacementType',
            '_position',
            '_pivot',
            '_rotation',
            '_scale',
            '_groupID',
            '_sortingOrder',
            '_mapLevel',
            '_onTerrainLayer',
            '_hidden',
            '_locked',
            '_superLocked',
            '_hue',
            '_brightness',
            '_saturation',
            '_opacity',
            '_tint',
            '_flipH',
            '_flipV',
            '_ignoreTimeOfDay',
            '_chromaKeyEnabled',
            '_chromaKeyColour',
            '_chromeKeyTolerance',
            '_lighting',
            '_hasDropShadow',
            '_blocksLight',
            '_animation',
            '_effects',
            '_effectsNew',
            '_alphaFriendlyCollider',
            '_blocking',
            '_chromaKeyReplacementColour',
            '_chromaKeyReplacementAlpha',
            '_uID',
            '_blockedByMovementBlockers',
            '_dropShadow',
            '_dropShadowLegacyUpgrade',
            '_ambience'
        ],
        'types': [
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            4,
            4,
            4,
            4,
            4,
            0,
            4,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            4,
            0,
            0,
            0,
            0,
            4,
            0,
            4,
            0,
            0,
            4,
            3,
            3,
            0,
            4,
            4,
            0,
            0,
            0,
            4,
            0,
            4
        ],
        'infos': [
            None,
            None,
            1,
            1,
            1,
            1,
            8,
            None,
            None,
            None,
            None,
            {'name': 'ArkenTile+TileType', 'library_id': 2},
            {'name': 'ArkenTileUpgrade+TileCategory', 'library_id': 2},
            {'name': 'MapOptions+ObjectPlacementType', 'library_id': 2},
            {'name': 'SVector2', 'library_id': 2},
            {'name': 'SVector2', 'library_id': 2},
            11,
            {'name': 'SVector2', 'library_id': 2},
            8,
            8,
            8,
            1,
            1,
            1,
            1,
            11,
            11,
            11,
            11,
            {'name': 'SVector3', 'library_id': 2},
            1,
            1,
            1,
            1,
            {'name': 'SVector3', 'library_id': 2},
            11,
            {'name': 'TileLightingProperties', 'library_id': 2},
            1,
            1,
            {'name': 'TileAnimationProperties', 'library_id': 2},
            'System.Collections.Generic.List`1[[IObjectEffect, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            1,
            {'name': 'TileBlockingProperties', 'library_id': 2},
            {'name': 'SVector3', 'library_id': 2},
            11,
            9,
            1,
            {'name': 'TileDropShadowProperties', 'library_id': 2},
            1,
            {'name': 'TileAmbienceProperties', 'library_id': 2}
        ],
        'library_id': 2
    },
    'ArkenTileUpgrade': {
        'name': 'ArkenTileUpgrade',
        'names': ['_name', '_pack', '_creator', '_category', '_legacyType', '_thumbnail', '_thumbnailScale', '_content'],
        'types': [1, 1, 1, 4, 4, 4, 0, 2],
        'infos': [
            None,
            None,
            None,
            {'name': 'ArkenTileUpgrade+TileCategory', 'library_id': 2},
            {'name': 'ArkenTile+TileType', 'library_id': 2},
            {'name': 'ArkenImage', 'library_id': 2},
            11,
            None
        ],
        'library_id': 2
    },
    'ArkenImage': {
        'name': 'ArkenImage',
        'names': ['_packImgX', '_packImgY', '_packImgChannels', '_packImageRAW'],
        'types': [0, 0, 0, 7],
        'infos': [8, 8, 8, 2],
        'library_id': 2
    },
    'ArkenTileMeta': {
        'name': 'ArkenTileMeta',
        'names': [
            '_category',
            '_tileType',
            '_tileCategory',
            '_thumbnail',
            '_thumbnailScale',
            '_variations',
            '_name',
            '_pack',
            '_creator',
            '_genre',
            '_subgenre',
            '_tags',
            '_starred',
            '_hideFromView',
            '_includedWorldPaths',
            '_official',
            '_prevPathIfDeleted',
            '_links',
            'ArkenBaseMeta+_name',
            'ArkenBaseMeta+_pack',
            'ArkenBaseMeta+_creator',
            'ArkenBaseMeta+_genre',
            'ArkenBaseMeta+_subgenre',
            'ArkenBaseMeta+_tags',
            'ArkenBaseMeta+_starred',
            'ArkenBaseMeta+_hideFromView',
            'ArkenBaseMeta+_includedWorldPaths',
            'ArkenBaseMeta+_official',
            'ArkenBaseMeta+_prevPathIfDeleted',
            'ArkenBaseMeta+_links',
            'LinkableContent+_links'
        ],
        'types': [1, 4, 4, 4, 0, 3, 1, 1, 1, 1, 1, 3, 0, 0, 3, 0, 1, 3, 1, 1, 1, 1, 1, 3, 0, 0, 3, 0, 1, 3, 3],
        'infos': [
            None,
            {'name': 'ArkenTile+TileType', 'library_id': 2},
            {'name': 'ArkenTileUpgrade+TileCategory', 'library_id': 2},
            {'name': 'ArkenImage', 'library_id': 2},
            11,
            'System.Collections.Generic.List`1[[ArkenTilePresetBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            None,
            None,
            None,
            None,
            None,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            1,
            1,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            1,
            None,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            None,
            None,
            None,
            None,
            None,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            1,
            1,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            1,
            None,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]'
        ],
        'library_id': 2
    },
    'System.Collections.Generic.List`1[[ArkenTilePresetBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]': {
        'name': 'System.Collections.Generic.List`1[[ArkenTilePresetBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
        'names': ['_items', '_size', '_version'],
        'types': [4, 0, 0],
        'infos': [
            {'name': 'ArkenTilePresetBase[]', 'library_id': 2},
            8,
            8
        ],
        'library_id': None
    },
    'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]': {
        'name': 'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
        'names': ['_items', '_size', '_version'],
        'types': [6, 0, 0],
        'infos': [None, 8, 8],
        'library_id': None
    },
    'ArkenMapUpgrade': {
        'name': 'ArkenMapUpgrade',
        'names': [
            '_name',
            '_pack',
            '_packCreator',
            '_lastModifiedDate',
            '_creator',
            '_creationDate',
            '_description',
            '_canBeCommercialized',
            '_tiles',
            '_timeOfDay',
            '_dropShadow',
            '_linkedPresets',
            '_bookmarks',
            '_fogLevelDataFull',
            '_gridType',
            '_gridDisplay',
            '_gridTransparency',
            '_gridColourR',
            '_gridColourG',
            '_gridColourB',
            '_gridBelowObjects',
            '_backgroundColour',
            '_fogEnabled',
            '_fogMode',
            '_fogPersists',
            '_fogColour',
            '_mapRotation',
            '_embeddedLinks',
            '_layersInOrder',
            '_importedTiles',
            '_useCustomAmbienceColour',
            '_customAmbientColour',
            '_useCustomLightIntensity',
            '_customLightIntensity',
            '_multilevelMap',
            '_playerScreenLocation',
            '_playerScreenSize',
            '_nextUID',
            '_gridEnabled',
            '_playerMapFollowUID',
            '_playerSplashScreen',
            '_startPointSetManually',
            '_mapRotationPlayer',
            '_playerMapFollowObject',
            '_mapBackgroundTexture'
        ],
        'types': [
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            0,
            3,
            0,
            4,
            4,
            3,
            3,
            4,
            4,
            0,
            0,
            0,
            0,
            0,
            4,
            0,
            4,
            0,
            4,
            0,
            3,
            0,
            3,
            0,
            4,
            0,
            0,
            0,
            4,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            1
        ],
        'infos': [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            1,
            'System.Collections.Generic.List`1[[ArkenMapTileUpgradeBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            11,
            {'name': 'MapDropShadowProperties', 'library_id': 2},
            {'name': 'SoundscapePreset[]', 'library_id': 2},
            'System.Collections.Generic.List`1[[MapBookmark, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            'System.Collections.Generic.Dictionary`2[[System.Int32, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089],[System.Collections.Generic.List`1[[FoW.FogOfWarChunk, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]], mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            {'name': 'MapOptions+GridType', 'library_id': 2},
            {'name': 'MapOptions+GridDisplay', 'library_id': 2},
            11,
            11,
            11,
            11,
            1,
            {'name': 'SVector3', 'library_id': 2},
            1,
            {'name': 'FogOfWarOptions+FogMode', 'library_id': 2},
            1,
            {'name': 'SVector3', 'library_id': 2},
            11,
            'System.Collections.Generic.List`1[[EmbeddedLink, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            1,
            'System.Collections.Generic.Dictionary`2[[ArkenTileUpgrade, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null],[System.Collections.Generic.List`1[[ArkenTilePresetBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]], mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            1,
            {'name': 'SVector3', 'library_id': 2},
            1,
            11,
            1,
            {'name': 'SVector2', 'library_id': 2},
            11,
            9,
            1,
            9,
            None,
            1,
            11,
            1,
            None
        ],
        'library_id': 2
    },
    'System.Collections.Generic.List`1[[ArkenMapTileUpgradeBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]': {
        'name': 'System.Collections.Generic.List`1[[ArkenMapTileUpgradeBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
        'names': ['_items', '_size', '_version'],
        'types': [4, 0, 0],
        'infos': [
            {'name': 'ArkenMapTileUpgradeBase[]', 'library_id': 2},
            8,
            8
        ],
        'library_id': None
    },
    'MapDropShadowProperties': {
        'name': 'MapDropShadowProperties',
        'names': [
            '_dropShadowDirection',
            '_dropShadowSize',
            '_dropShadowDistance',
            '_dropShadowStrength',
            '_dropShadowFollowsSun',
            '_dropShadowFollowsSunNorthernHemisphere',
            '_dropShadowsEnabled'
        ],
        'types': [0, 0, 0, 0, 0, 0, 0],
        'infos': [8, 11, 11, 11, 1, 1, 1],
        'library_id': 2
    },
    'System.Collections.Generic.List`1[[MapBookmark, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]': {
        'name': 'System.Collections.Generic.List`1[[MapBookmark, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
        'names': ['_items', '_size', '_version'],
        'types': [4, 0, 0],
        'infos': [
            {'name': 'MapBookmark[]', 'library_id': 2},
            8,
            8
        ],
        'library_id': None
    },
    'System.Collections.Generic.Dictionary`2[[System.Int32, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089],[System.Collections.Generic.List`1[[FoW.FogOfWarChunk, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]], mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]': {
        'name': 'System.Collections.Generic.Dictionary`2[[System.Int32, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089],[System.Collections.Generic.List`1[[FoW.FogOfWarChunk, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]], mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
        'names': ['Version', 'Comparer', 'HashSize'],
        'types': [0, 3, 0],
        'infos': [
            8,
            'System.Collections.Generic.GenericEqualityComparer`1[[System.Int32, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            8
        ],
        'library_id': None
    },
    'System.Collections.Generic.GenericEqualityComparer`1[[System.Int32, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]': {
        'name': 'System.Collections.Generic.GenericEqualityComparer`1[[System.Int32, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
        'names': [],
        'types': [],
        'infos': [],
        'library_id': None
    },
    'MapOptions+GridDisplay': {
        'name': 'MapOptions+GridDisplay',
        'names': ['value__'],
        'types': [0],
        'infos': [8],
        'library_id': 2
    },
    'FogOfWarOptions+FogMode': {
        'name': 'FogOfWarOptions+FogMode',
        'names': ['value__'],
        'types': [0],
        'infos': [8],
        'library_id': 2
    },
    'System.Collections.Generic.List`1[[EmbeddedLink, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]': {
        'name': 'System.Collections.Generic.List`1[[EmbeddedLink, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
        'names': ['_items', '_size', '_version'],
        'types': [4, 0, 0],
        'infos': [
            {'name': 'EmbeddedLink[]', 'library_id': 2},
            8,
            8
        ],
        'library_id': None
    },
    'System.Collections.Generic.Dictionary`2[[ArkenTileUpgrade, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null],[System.Collections.Generic.List`1[[ArkenTilePresetBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]], mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]': {
        'name': 'System.Collections.Generic.Dictionary`2[[ArkenTileUpgrade, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null],[System.Collections.Generic.List`1[[ArkenTilePresetBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]], mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
        'names': ['Version', 'Comparer', 'HashSize'],
        'types': [0, 3, 0],
        'infos': [
            8,
            'System.Collections.Generic.ObjectEqualityComparer`1[[ArkenTileUpgrade, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            8
        ],
        'library_id': None
    },
    'System.Collections.Generic.ObjectEqualityComparer`1[[ArkenTileUpgrade, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]': {
        'name': 'System.Collections.Generic.ObjectEqualityComparer`1[[ArkenTileUpgrade, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
        'names': [],
        'types': [],
        'infos': [],
        'library_id': None
    },
    'ArkenMapMeta': {
        'name': 'ArkenMapMeta',
        'names': [
            '_mapName',
            '_mapCreator',
            '_mapType',
            '_creationDate',
            '_lastModified',
            '_description',
            '_canBeCommercialized',
            '_favourited',
            '_isAutosave',
            '_autosavePath',
            '_thumbnail',
            '_bookmarks',
            '_name',
            '_pack',
            '_creator',
            '_genre',
            '_subgenre',
            '_tags',
            '_starred',
            '_hideFromView',
            '_includedWorldPaths',
            '_official',
            '_prevPathIfDeleted',
            '_links',
            'ArkenBaseMeta+_name',
            'ArkenBaseMeta+_pack',
            'ArkenBaseMeta+_creator',
            'ArkenBaseMeta+_genre',
            'ArkenBaseMeta+_subgenre',
            'ArkenBaseMeta+_tags',
            'ArkenBaseMeta+_starred',
            'ArkenBaseMeta+_hideFromView',
            'ArkenBaseMeta+_includedWorldPaths',
            'ArkenBaseMeta+_official',
            'ArkenBaseMeta+_prevPathIfDeleted',
            'ArkenBaseMeta+_links',
            'LinkableContent+_links'
        ],
        'types': [
            1,
            1,
            4,
            1,
            1,
            1,
            0,
            0,
            0,
            1,
            4,
            3,
            1,
            1,
            1,
            1,
            1,
            3,
            0,
            0,
            3,
            0,
            1,
            3,
            1,
            1,
            1,
            1,
            1,
            3,
            0,
            0,
            3,
            0,
            1,
            3,
            3
        ],
        'infos': [
            None,
            None,
            {'name': 'MapOptions+MapModule', 'library_id': 2},
            None,
            None,
            None,
            1,
            1,
            1,
            None,
            {'name': 'ArkenImage', 'library_id': 2},
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            None,
            None,
            None,
            None,
            None,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            1,
            1,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            1,
            None,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            None,
            None,
            None,
            None,
            None,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            1,
            1,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            1,
            None,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]'
        ],
        'library_id': 2
    },
    'MapOptions+MapModule': {
        'name': 'MapOptions+MapModule',
        'names': ['value__'],
        'types': [0],
        'infos': [8],
        'library_id': 2
    },
    'ArkenTilePresetContentLink': {
        'name': 'ArkenTilePresetContentLink',
        'names': [
            '_contentBasePath',
            '_contentType',
            '_onlyShowOnMyLevel',
            '_useDefaultTint',
            '_visibleOnLowerLevels',
            '_name',
            '_editable',
            '_visibleInLibrary',
            '_official',
            '_imported',
            '_version',
            '_tileName',
            '_tilePack',
            '_tileCreator',
            '_tilePath',
            '_tileType',
            '_category',
            '_defaultPlacementType',
            '_position',
            '_pivot',
            '_rotation',
            '_scale',
            '_groupID',
            '_sortingOrder',
            '_mapLevel',
            '_onTerrainLayer',
            '_hidden',
            '_locked',
            '_superLocked',
            '_hue',
            '_brightness',
            '_saturation',
            '_opacity',
            '_tint',
            '_flipH',
            '_flipV',
            '_ignoreTimeOfDay',
            '_chromaKeyEnabled',
            '_chromaKeyColour',
            '_chromeKeyTolerance',
            '_lighting',
            '_hasDropShadow',
            '_blocksLight',
            '_animation',
            '_effectsNew',
            '_alphaFriendlyCollider',
            '_blocking',
            '_chromaKeyReplacementColour',
            '_chromaKeyReplacementAlpha',
            '_uID',
            '_blockedByMovementBlockers',
            'ArkenTilePresetBase+_name',
            'ArkenTilePresetBase+_baseName',
            'ArkenTilePresetBase+_editable',
            'ArkenTilePresetBase+_visibleInLibrary',
            'ArkenTilePresetBase+_official',
            'ArkenTilePresetBase+_imported',
            'ArkenTilePresetBase+_version',
            'ArkenTilePresetBase+_tileName',
            'ArkenTilePresetBase+_tilePack',
            'ArkenTilePresetBase+_tileCreator',
            'ArkenTilePresetBase+_tilePath',
            'ArkenTilePresetBase+_tileType',
            'ArkenTilePresetBase+_category',
            'ArkenTilePresetBase+_defaultPlacementType',
            'ArkenTilePresetBase+_position',
            'ArkenTilePresetBase+_pivot',
            'ArkenTilePresetBase+_rotation',
            'ArkenTilePresetBase+_scale',
            'ArkenTilePresetBase+_groupID',
            'ArkenTilePresetBase+_sortingOrder',
            'ArkenTilePresetBase+_mapLevel',
            'ArkenTilePresetBase+_onTerrainLayer',
            'ArkenTilePresetBase+_hidden',
            'ArkenTilePresetBase+_locked',
            'ArkenTilePresetBase+_superLocked',
            'ArkenTilePresetBase+_hue',
            'ArkenTilePresetBase+_brightness',
            'ArkenTilePresetBase+_saturation',
            'ArkenTilePresetBase+_opacity',
            'ArkenTilePresetBase+_tint',
            'ArkenTilePresetBase+_flipH',
            'ArkenTilePresetBase+_flipV',
            'ArkenTilePresetBase+_ignoreTimeOfDay',
            'ArkenTilePresetBase+_chromaKeyEnabled',
            'ArkenTilePresetBase+_chromaKeyColour',
            'ArkenTilePresetBase+_chromeKeyTolerance',
            'ArkenTilePresetBase+_lighting',
            'ArkenTilePresetBase+_hasDropShadow',
            'ArkenTilePresetBase+_blocksLight',
            'ArkenTilePresetBase+_animation',
            'ArkenTilePresetBase+_effects',
            'ArkenTilePresetBase+_effectsNew',
            'ArkenTilePresetBase+_alphaFriendlyCollider',
            'ArkenTilePresetBase+_blocking',
            'ArkenTilePresetBase+_chromaKeyReplacementColour',
            'ArkenTilePresetBase+_chromaKeyReplacementAlpha',
            'ArkenTilePresetBase+_uID',
            'ArkenTilePresetBase+_blockedByMovementBlockers',
            'ArkenTilePresetBase+_dropShadow',
            'ArkenTilePresetBase+_dropShadowLegacyUpgrade',
            'ArkenTilePresetBase+_ambience'
        ],
        'types': [
            1,
            1,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            4,
            4,
            4,
            4,
            4,
            0,
            4,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            4,
            0,
            0,
            0,
            0,
            4,
            0,
            4,
            0,
            0,
            4,
            3,
            0,
            4,
            4,
            0,
            0,
            0,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            4,
            4,
            4,
            4,
            4,
            0,
            4,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            4,
            0,
            0,
            0,
            0,
            4,
            0,
            4,
            0,
            0,
            4,
            3,
            3,
            0,
            4,
            4,
            0,
            0,
            0,
            4,
            0,
            4
        ],
        'infos': [
            None,
            None,
            1,
            1,
            1,
            None,
            1,
            1,
            1,
            1,
            8,
            None,
            None,
            None,
            None,
            {'name': 'ArkenTile+TileType', 'library_id': 2},
            {'name': 'ArkenTileUpgrade+TileCategory', 'library_id': 2},
            {'name': 'MapOptions+ObjectPlacementType', 'library_id': 2},
            {'name': 'SVector2', 'library_id': 2},
            {'name': 'SVector2', 'library_id': 2},
            11,
            {'name': 'SVector2', 'library_id': 2},
            8,
            8,
            8,
            1,
            1,
            1,
            1,
            11,
            11,
            11,
            11,
            {'name': 'SVector3', 'library_id': 2},
            1,
            1,
            1,
            1,
            {'name': 'SVector3', 'library_id': 2},
            11,
            {'name': 'TileLightingProperties', 'library_id': 2},
            1,
            1,
            {'name': 'TileAnimationProperties', 'library_id': 2},
            'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            1,
            {'name': 'TileBlockingProperties', 'library_id': 2},
            {'name': 'SVector3', 'library_id': 2},
            11,
            9,
            1,
            None,
            None,
            1,
            1,
            1,
            1,
            8,
            None,
            None,
            None,
            None,
            {'name': 'ArkenTile+TileType', 'library_id': 2},
            {'name': 'ArkenTileUpgrade+TileCategory', 'library_id': 2},
            {'name': 'MapOptions+ObjectPlacementType', 'library_id': 2},
            {'name': 'SVector2', 'library_id': 2},
            {'name': 'SVector2', 'library_id': 2},
            11,
            {'name': 'SVector2', 'library_id': 2},
            8,
            8,
            8,
            1,
            1,
            1,
            1,
            11,
            11,
            11,
            11,
            {'name': 'SVector3', 'library_id': 2},
            1,
            1,
            1,
            1,
            {'name': 'SVector3', 'library_id': 2},
            11,
            {'name': 'TileLightingProperties', 'library_id': 2},
            1,
            1,
            {'name': 'TileAnimationProperties', 'library_id': 2},
            'System.Collections.Generic.List`1[[IObjectEffect, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
            1,
            {'name': 'TileBlockingProperties', 'library_id': 2},
            {'name': 'SVector3', 'library_id': 2},
            11,
            9,
            1,
            {'name': 'TileDropShadowProperties', 'library_id': 2},
            1,
            {'name': 'TileAmbienceProperties', 'library_id': 2}
        ],
        'library_id': 2
    },
    'ArkenNoteFieldSize': {
        'name': 'ArkenNoteFieldSize',
        'names': [
            '_squareSize',
            '_squareSizeNew',
            '_headingColour',
            '_name',
            '_visibleToPlayers',
            '_UID',
            'ArkenNoteField+_name',
            'ArkenNoteField+_visibleToPlayers',
            'ArkenNoteField+_UID'
        ],
        'types': [0, 0, 4, 1, 3, 0, 1, 3, 0],
        'infos': [
            8,
            11,
            {'name': 'SVector3', 'library_id': 2},
            None,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            8,
            None,
            'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
            8
        ],
        'library_id': 2
    }
}

DEFAULTS = {
    'wall': {
        'id': 1,
        'class': 'ArkenMapTileUpgradeBase',
        'inline': False,
        'members': {
            '_tileInfo': {
                'id': 2,
                'class': 'ArkenTilePresetRepeatable',
                'inline': False,
                'members': {
                    '_points': {
                        'id': 3,
                        'class': 'System.Collections.Generic.List`1[[SVector2, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {
                            '_items': {
                                'id': 4,
                                'array': [
                                    4,
                                    {'name': 'SVector2', 'library_id': 2}
                                ],
                                'items': [
                                    {
                                        'id': 5,
                                        'class': 'SVector2',
                                        'inline': False,
                                        'members': {'x': 0.0, 'y': 0.0}
                                    },
                                    {
                                        'id': 6,
                                        'class': 'SVector2',
                                        'inline': False,
                                        'members': {'x': 0.0, 'y': 0.0}
                                    },
                                    None,
                                    None
                                ]
                            },
                            '_size': 2,
                            '_version': 2
                        }
                    },
                    '_width': 0.10000000149011612,
                    '_worldSpaceTexture': False,
                    '_tileScale': 0.0,
                    '_startTaper': 1.0,
                    '_endTaper': 1.0,
                    '_scrollPos': 0.0,
                    '_fadeLine': False,
                    '_fadeLineFlipDirection': False,
                    '_fadeStartPoint': 0.5,
                    '_loop': False,
                    '_name': 'Barrier',
                    '_editable': True,
                    '_visibleInLibrary': True,
                    '_official': False,
                    '_imported': False,
                    '_version': 0,
                    '_tileName': 'Barrier',
                    '_tilePack': 'MastersToolkit',
                    '_tileCreator': 'Arkenforge',
                    '_tilePath': None,
                    '_tileType': {
                        'id': 7,
                        'class': 'ArkenTile+TileType',
                        'inline': True,
                        'members': {'value__': 9}
                    },
                    '_category': {
                        'id': 8,
                        'class': 'ArkenTileUpgrade+TileCategory',
                        'inline': True,
                        'members': {'value__': 0}
                    },
                    '_defaultPlacementType': {
                        'id': 9,
                        'class': 'MapOptions+ObjectPlacementType',
                        'inline': True,
                        'members': {'value__': 2}
                    },
                    '_position': {
                        'id': 10,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 0.0, 'y': 0.0}
                    },
                    '_pivot': {
                        'id': 11,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 0.0, 'y': 0.0}
                    },
                    '_rotation': 0.0,
                    '_scale': {
                        'id': 12,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0}
                    },
                    '_groupID': -1,
                    '_sortingOrder': 1,
                    '_mapLevel': 0,
                    '_onTerrainLayer': False,
                    '_hidden': False,
                    '_locked': False,
                    '_superLocked': False,
                    '_hue': 0.5,
                    '_brightness': 0.5,
                    '_saturation': 0.5,
                    '_opacity': 1.0,
                    '_tint': {
                        'id': 13,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_flipH': False,
                    '_flipV': False,
                    '_ignoreTimeOfDay': False,
                    '_chromaKeyEnabled': False,
                    '_chromaKeyColour': {
                        'id': 14,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_chromeKeyTolerance': 0.07500000298023224,
                    '_lighting': {
                        'id': 15,
                        'class': 'TileLightingProperties',
                        'inline': False,
                        'members': {
                            '_hasLight': False,
                            '_lightRadius': {
                                'id': 16,
                                'class': 'System.Collections.Generic.List`1[[System.Single, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                                'inline': False,
                                'members': {
                                    '_items': {
                                        'id': 17,
                                        'array': [0, 11],
                                        'items': [12.799999237060547, 0.0, 0.0, 0.0]
                                    },
                                    '_size': 1,
                                    '_version': 1
                                }
                            },
                            '_lightR': 0.3409999907016754,
                            '_lightG': 0.3179999887943268,
                            '_lightB': 0.07100000232458115,
                            '_visibleThroughFog': False,
                            '_flicker': False,
                            '_darkness': False,
                            '_qualitySetting': 0,
                            '_fov': 360,
                            '_lightUpdates': True,
                            '_lightIntensity': 1.0,
                            '_lightDirection': 0
                        }
                    },
                    '_hasDropShadow': False,
                    '_blocksLight': False,
                    '_animation': {
                        'id': 18,
                        'class': 'TileAnimationProperties',
                        'inline': False,
                        'members': {
                            '_playing': True,
                            '_currentFrame': 0,
                            '_framesPerSecond': 30.0,
                            '_noOfFrames': 0.0,
                            '_triggered': False,
                            '_startFrame': 0.0,
                            '_endFrame': 0.0,
                            '_destroyAfterOnePlay': False,
                            '_delay': False,
                            '_delayTime': 0.0,
                            '_delayVariance': 0.0,
                            '_deactivateOnDelay': False,
                            '_ghostTileFrame': 0
                        }
                    },
                    '_effectsNew': {
                        'id': 19,
                        'class': 'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {
                            '_items': {
                                'id': 20,
                                'array': [
                                    4,
                                    {'name': 'ObjectEffectBase', 'library_id': 2}
                                ],
                                'items': []
                            },
                            '_size': 0,
                            '_version': 0
                        }
                    },
                    '_alphaFriendlyCollider': False,
                    '_blocking': {
                        'id': 21,
                        'class': 'TileBlockingProperties',
                        'inline': False,
                        'members': {
                            '_blockingEnabled': True,
                            '_light': True,
                            '_vision': True,
                            '_sound': False,
                            '_movement': True,
                            '_oneWay': False,
                            '_oneWayDirection': False,
                            '_toggleable': False,
                            '_colliderMode': 0
                        }
                    },
                    '_chromaKeyReplacementColour': {
                        'id': 22,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_chromaKeyReplacementAlpha': 0.0,
                    '_uID': 1,
                    '_blockedByMovementBlockers': False,
                    'ArkenTilePresetBase+_name': 'Barrier',
                    'ArkenTilePresetBase+_baseName': None,
                    'ArkenTilePresetBase+_editable': True,
                    'ArkenTilePresetBase+_visibleInLibrary': True,
                    'ArkenTilePresetBase+_official': False,
                    'ArkenTilePresetBase+_imported': False,
                    'ArkenTilePresetBase+_version': 0,
                    'ArkenTilePresetBase+_tileName': 'Barrier',
                    'ArkenTilePresetBase+_tilePack': 'MastersToolkit',
                    'ArkenTilePresetBase+_tileCreator': 'Arkenforge',
                    'ArkenTilePresetBase+_tilePath': None,
                    'ArkenTilePresetBase+_tileType': {
                        'id': 23,
                        'class': 'ArkenTile+TileType',
                        'inline': True,
                        'members': {'value__': 9}
                    },
                    'ArkenTilePresetBase+_category': {
                        'id': 24,
                        'class': 'ArkenTileUpgrade+TileCategory',
                        'inline': True,
                        'members': {'value__': 0}
                    },
                    'ArkenTilePresetBase+_defaultPlacementType': {
                        'id': 25,
                        'class': 'MapOptions+ObjectPlacementType',
                        'inline': True,
                        'members': {'value__': 2}
                    },
                    'ArkenTilePresetBase+_position': {'use': 10},
                    'ArkenTilePresetBase+_pivot': {'use': 11},
                    'ArkenTilePresetBase+_rotation': 0.0,
                    'ArkenTilePresetBase+_scale': {'use': 12},
                    'ArkenTilePresetBase+_groupID': -1,
                    'ArkenTilePresetBase+_sortingOrder': 1,
                    'ArkenTilePresetBase+_mapLevel': 0,
                    'ArkenTilePresetBase+_onTerrainLayer': False,
                    'ArkenTilePresetBase+_hidden': False,
                    'ArkenTilePresetBase+_locked': False,
                    'ArkenTilePresetBase+_superLocked': False,
                    'ArkenTilePresetBase+_hue': 0.5,
                    'ArkenTilePresetBase+_brightness': 0.5,
                    'ArkenTilePresetBase+_saturation': 0.5,
                    'ArkenTilePresetBase+_opacity': 1.0,
                    'ArkenTilePresetBase+_tint': {'use': 13},
                    'ArkenTilePresetBase+_flipH': False,
                    'ArkenTilePresetBase+_flipV': False,
                    'ArkenTilePresetBase+_ignoreTimeOfDay': False,
                    'ArkenTilePresetBase+_chromaKeyEnabled': False,
                    'ArkenTilePresetBase+_chromaKeyColour': {'use': 14},
                    'ArkenTilePresetBase+_chromeKeyTolerance': 0.07500000298023224,
                    'ArkenTilePresetBase+_lighting': {'use': 15},
                    'ArkenTilePresetBase+_hasDropShadow': False,
                    'ArkenTilePresetBase+_blocksLight': False,
                    'ArkenTilePresetBase+_animation': {'use': 18},
                    'ArkenTilePresetBase+_effects': {
                        'id': 26,
                        'class': 'System.Collections.Generic.List`1[[IObjectEffect, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {
                            '_items': {
                                'id': 27,
                                'array': [
                                    4,
                                    {'name': 'IObjectEffect', 'library_id': 2}
                                ],
                                'items': []
                            },
                            '_size': 0,
                            '_version': 0
                        }
                    },
                    'ArkenTilePresetBase+_effectsNew': {'use': 19},
                    'ArkenTilePresetBase+_alphaFriendlyCollider': False,
                    'ArkenTilePresetBase+_blocking': {'use': 21},
                    'ArkenTilePresetBase+_chromaKeyReplacementColour': {'use': 22},
                    'ArkenTilePresetBase+_chromaKeyReplacementAlpha': 0.0,
                    'ArkenTilePresetBase+_uID': 1,
                    'ArkenTilePresetBase+_blockedByMovementBlockers': False,
                    'ArkenTilePresetBase+_dropShadow': {
                        'id': 28,
                        'class': 'TileDropShadowProperties',
                        'inline': False,
                        'members': {
                            '_shadowActive': True,
                            '_shadowStrengthUsesMapDefault': False,
                            '_shadowStrength': 1.0,
                            '_shadowSizeUsesMapDefault': True,
                            '_shadowSize': 1.0499999523162842,
                            '_shadowDistanceUsesMapDefault': False,
                            '_shadowDistance': 0.0,
                            '_shadowDirectionUsesMapDefault': True,
                            '_shadowDirection': 1,
                            '_followsSunUsesMapDefault': True,
                            '_dropShadowsFollowSun': False
                        }
                    },
                    'ArkenTilePresetBase+_dropShadowLegacyUpgrade': True,
                    'ArkenTilePresetBase+_ambience': {
                        'id': 29,
                        'class': 'TileAmbienceProperties',
                        'inline': False,
                        'members': {
                            '_active': False,
                            '_audioPath': None,
                            '_radius': 12.799999237060547,
                            '_falloffRadius': 25.599998474121094,
                            '_volume': 1.0,
                            '_playWhenHidden': True,
                            '_activeTimeMin': 0.0,
                            '_activeTimeMax': 1.0,
                            '_playOnAllLevels': False
                        }
                    }
                }
            },
            '_placementType': {
                'id': 30,
                'class': 'MapOptions+ObjectPlacementType',
                'inline': True,
                'members': {'value__': 3}
            },
            '_brushType': {
                'id': 31,
                'class': 'MapOptions+PlacementType',
                'inline': True,
                'members': {'value__': 5}
            },
            '_gridType': {
                'id': 32,
                'class': 'MapOptions+GridType',
                'inline': True,
                'members': {'value__': 0}
            },
            'spriteWidth': 32.0,
            'spriteRatio': 1.0,
            '_trueSize': -1.0,
            '_additionalData': None
        }
    },
    'door': {
        'id': 1,
        'class': 'ArkenMapTileUpgradeBase',
        'inline': False,
        'members': {
            '_tileInfo': {
                'id': 2,
                'class': 'ArkenTilePresetRepeatable',
                'inline': False,
                'members': {
                    '_points': {
                        'id': 3,
                        'class': 'System.Collections.Generic.List`1[[SVector2, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {
                            '_items': {
                                'id': 4,
                                'array': [
                                    4,
                                    {'name': 'SVector2', 'library_id': 2}
                                ],
                                'items': [
                                    {
                                        'id': 5,
                                        'class': 'SVector2',
                                        'inline': False,
                                        'members': {'x': 0.0, 'y': 0.0}
                                    },
                                    {
                                        'id': 6,
                                        'class': 'SVector2',
                                        'inline': False,
                                        'members': {'x': 0.0, 'y': 0.0}
                                    },
                                    None,
                                    None
                                ]
                            },
                            '_size': 2,
                            '_version': 2
                        }
                    },
                    '_width': 0.10000000149011612,
                    '_worldSpaceTexture': False,
                    '_tileScale': 0.0,
                    '_startTaper': 1.0,
                    '_endTaper': 1.0,
                    '_scrollPos': 0.0,
                    '_fadeLine': False,
                    '_fadeLineFlipDirection': False,
                    '_fadeStartPoint': 0.5,
                    '_loop': False,
                    '_name': 'Barrier',
                    '_editable': True,
                    '_visibleInLibrary': True,
                    '_official': False,
                    '_imported': False,
                    '_version': 0,
                    '_tileName': 'Barrier',
                    '_tilePack': 'MastersToolkit',
                    '_tileCreator': 'Arkenforge',
                    '_tilePath': None,
                    '_tileType': {
                        'id': 7,
                        'class': 'ArkenTile+TileType',
                        'inline': True,
                        'members': {'value__': 9}
                    },
                    '_category': {
                        'id': 8,
                        'class': 'ArkenTileUpgrade+TileCategory',
                        'inline': True,
                        'members': {'value__': 0}
                    },
                    '_defaultPlacementType': {
                        'id': 9,
                        'class': 'MapOptions+ObjectPlacementType',
                        'inline': True,
                        'members': {'value__': 2}
                    },
                    '_position': {
                        'id': 10,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 0.0, 'y': 0.0}
                    },
                    '_pivot': {
                        'id': 11,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 0.0, 'y': 0.0}
                    },
                    '_rotation': 0.0,
                    '_scale': {
                        'id': 12,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0}
                    },
                    '_groupID': -1,
                    '_sortingOrder': 1,
                    '_mapLevel': 0,
                    '_onTerrainLayer': False,
                    '_hidden': False,
                    '_locked': False,
                    '_superLocked': False,
                    '_hue': 0.5,
                    '_brightness': 0.5,
                    '_saturation': 0.5,
                    '_opacity': 1.0,
                    '_tint': {
                        'id': 13,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_flipH': False,
                    '_flipV': False,
                    '_ignoreTimeOfDay': False,
                    '_chromaKeyEnabled': False,
                    '_chromaKeyColour': {
                        'id': 14,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_chromeKeyTolerance': 0.07500000298023224,
                    '_lighting': {
                        'id': 15,
                        'class': 'TileLightingProperties',
                        'inline': False,
                        'members': {
                            '_hasLight': False,
                            '_lightRadius': {
                                'id': 16,
                                'class': 'System.Collections.Generic.List`1[[System.Single, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                                'inline': False,
                                'members': {
                                    '_items': {
                                        'id': 17,
                                        'array': [0, 11],
                                        'items': [12.799999237060547, 0.0, 0.0, 0.0]
                                    },
                                    '_size': 1,
                                    '_version': 1
                                }
                            },
                            '_lightR': 0.3409999907016754,
                            '_lightG': 0.3179999887943268,
                            '_lightB': 0.07100000232458115,
                            '_visibleThroughFog': False,
                            '_flicker': False,
                            '_darkness': False,
                            '_qualitySetting': 0,
                            '_fov': 360,
                            '_lightUpdates': True,
                            '_lightIntensity': 1.0,
                            '_lightDirection': 0
                        }
                    },
                    '_hasDropShadow': False,
                    '_blocksLight': False,
                    '_animation': {
                        'id': 18,
                        'class': 'TileAnimationProperties',
                        'inline': False,
                        'members': {
                            '_playing': True,
                            '_currentFrame': 0,
                            '_framesPerSecond': 30.0,
                            '_noOfFrames': 0.0,
                            '_triggered': False,
                            '_startFrame': 0.0,
                            '_endFrame': 0.0,
                            '_destroyAfterOnePlay': False,
                            '_delay': False,
                            '_delayTime': 0.0,
                            '_delayVariance': 0.0,
                            '_deactivateOnDelay': False,
                            '_ghostTileFrame': 0
                        }
                    },
                    '_effectsNew': {
                        'id': 19,
                        'class': 'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {
                            '_items': {
                                'id': 20,
                                'array': [
                                    4,
                                    {'name': 'ObjectEffectBase', 'library_id': 2}
                                ],
                                'items': []
                            },
                            '_size': 0,
                            '_version': 0
                        }
                    },
                    '_alphaFriendlyCollider': False,
                    '_blocking': {
                        'id': 21,
                        'class': 'TileBlockingProperties',
                        'inline': False,
                        'members': {
                            '_blockingEnabled': True,
                            '_light': True,
                            '_vision': True,
                            '_sound': False,
                            '_movement': False,
                            '_oneWay': False,
                            '_oneWayDirection': False,
                            '_toggleable': True,
                            '_colliderMode': 0
                        }
                    },
                    '_chromaKeyReplacementColour': {
                        'id': 22,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_chromaKeyReplacementAlpha': 0.0,
                    '_uID': 1,
                    '_blockedByMovementBlockers': False,
                    'ArkenTilePresetBase+_name': 'Barrier',
                    'ArkenTilePresetBase+_baseName': None,
                    'ArkenTilePresetBase+_editable': True,
                    'ArkenTilePresetBase+_visibleInLibrary': True,
                    'ArkenTilePresetBase+_official': False,
                    'ArkenTilePresetBase+_imported': False,
                    'ArkenTilePresetBase+_version': 0,
                    'ArkenTilePresetBase+_tileName': 'Barrier',
                    'ArkenTilePresetBase+_tilePack': 'MastersToolkit',
                    'ArkenTilePresetBase+_tileCreator': 'Arkenforge',
                    'ArkenTilePresetBase+_tilePath': None,
                    'ArkenTilePresetBase+_tileType': {
                        'id': 23,
                        'class': 'ArkenTile+TileType',
                        'inline': True,
                        'members': {'value__': 9}
                    },
                    'ArkenTilePresetBase+_category': {
                        'id': 24,
                        'class': 'ArkenTileUpgrade+TileCategory',
                        'inline': True,
                        'members': {'value__': 0}
                    },
                    'ArkenTilePresetBase+_defaultPlacementType': {
                        'id': 25,
                        'class': 'MapOptions+ObjectPlacementType',
                        'inline': True,
                        'members': {'value__': 2}
                    },
                    'ArkenTilePresetBase+_position': {'use': 10},
                    'ArkenTilePresetBase+_pivot': {'use': 11},
                    'ArkenTilePresetBase+_rotation': 0.0,
                    'ArkenTilePresetBase+_scale': {'use': 12},
                    'ArkenTilePresetBase+_groupID': -1,
                    'ArkenTilePresetBase+_sortingOrder': 1,
                    'ArkenTilePresetBase+_mapLevel': 0,
                    'ArkenTilePresetBase+_onTerrainLayer': False,
                    'ArkenTilePresetBase+_hidden': False,
                    'ArkenTilePresetBase+_locked': False,
                    'ArkenTilePresetBase+_superLocked': False,
                    'ArkenTilePresetBase+_hue': 0.5,
                    'ArkenTilePresetBase+_brightness': 0.5,
                    'ArkenTilePresetBase+_saturation': 0.5,
                    'ArkenTilePresetBase+_opacity': 1.0,
                    'ArkenTilePresetBase+_tint': {'use': 13},
                    'ArkenTilePresetBase+_flipH': False,
                    'ArkenTilePresetBase+_flipV': False,
                    'ArkenTilePresetBase+_ignoreTimeOfDay': False,
                    'ArkenTilePresetBase+_chromaKeyEnabled': False,
                    'ArkenTilePresetBase+_chromaKeyColour': {'use': 14},
                    'ArkenTilePresetBase+_chromeKeyTolerance': 0.07500000298023224,
                    'ArkenTilePresetBase+_lighting': {'use': 15},
                    'ArkenTilePresetBase+_hasDropShadow': False,
                    'ArkenTilePresetBase+_blocksLight': False,
                    'ArkenTilePresetBase+_animation': {'use': 18},
                    'ArkenTilePresetBase+_effects': {
                        'id': 26,
                        'class': 'System.Collections.Generic.List`1[[IObjectEffect, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {
                            '_items': {
                                'id': 27,
                                'array': [
                                    4,
                                    {'name': 'IObjectEffect', 'library_id': 2}
                                ],
                                'items': []
                            },
                            '_size': 0,
                            '_version': 0
                        }
                    },
                    'ArkenTilePresetBase+_effectsNew': {'use': 19},
                    'ArkenTilePresetBase+_alphaFriendlyCollider': False,
                    'ArkenTilePresetBase+_blocking': {'use': 21},
                    'ArkenTilePresetBase+_chromaKeyReplacementColour': {'use': 22},
                    'ArkenTilePresetBase+_chromaKeyReplacementAlpha': 0.0,
                    'ArkenTilePresetBase+_uID': 1,
                    'ArkenTilePresetBase+_blockedByMovementBlockers': False,
                    'ArkenTilePresetBase+_dropShadow': {
                        'id': 28,
                        'class': 'TileDropShadowProperties',
                        'inline': False,
                        'members': {
                            '_shadowActive': True,
                            '_shadowStrengthUsesMapDefault': False,
                            '_shadowStrength': 1.0,
                            '_shadowSizeUsesMapDefault': True,
                            '_shadowSize': 1.0499999523162842,
                            '_shadowDistanceUsesMapDefault': False,
                            '_shadowDistance': 0.0,
                            '_shadowDirectionUsesMapDefault': True,
                            '_shadowDirection': 1,
                            '_followsSunUsesMapDefault': True,
                            '_dropShadowsFollowSun': False
                        }
                    },
                    'ArkenTilePresetBase+_dropShadowLegacyUpgrade': True,
                    'ArkenTilePresetBase+_ambience': {
                        'id': 29,
                        'class': 'TileAmbienceProperties',
                        'inline': False,
                        'members': {
                            '_active': False,
                            '_audioPath': None,
                            '_radius': 12.799999237060547,
                            '_falloffRadius': 25.599998474121094,
                            '_volume': 1.0,
                            '_playWhenHidden': True,
                            '_activeTimeMin': 0.0,
                            '_activeTimeMax': 1.0,
                            '_playOnAllLevels': False
                        }
                    }
                }
            },
            '_placementType': {
                'id': 30,
                'class': 'MapOptions+ObjectPlacementType',
                'inline': True,
                'members': {'value__': 3}
            },
            '_brushType': {
                'id': 31,
                'class': 'MapOptions+PlacementType',
                'inline': True,
                'members': {'value__': 5}
            },
            '_gridType': {
                'id': 32,
                'class': 'MapOptions+GridType',
                'inline': True,
                'members': {'value__': 0}
            },
            'spriteWidth': 32.0,
            'spriteRatio': 1.0,
            '_trueSize': -1.0,
            '_additionalData': None
        }
    },
    'light': {
        'id': 1,
        'class': 'ArkenMapTileUpgradeBase',
        'inline': False,
        'members': {
            '_tileInfo': {
                'id': 2,
                'class': 'ArkenTilePresetBase',
                'inline': False,
                'members': {
                    '_name': 'Light Source',
                    '_baseName': None,
                    '_editable': True,
                    '_visibleInLibrary': True,
                    '_official': False,
                    '_imported': False,
                    '_version': 0,
                    '_tileName': 'Light Source',
                    '_tilePack': 'MastersToolkit',
                    '_tileCreator': 'Arkenforge',
                    '_tilePath': None,
                    '_tileType': {
                        'id': 3,
                        'class': 'ArkenTile+TileType',
                        'inline': True,
                        'members': {'value__': 8}
                    },
                    '_category': {
                        'id': 4,
                        'class': 'ArkenTileUpgrade+TileCategory',
                        'inline': True,
                        'members': {'value__': 0}
                    },
                    '_defaultPlacementType': {
                        'id': 5,
                        'class': 'MapOptions+ObjectPlacementType',
                        'inline': True,
                        'members': {'value__': 2}
                    },
                    '_position': {
                        'id': 6,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 0.0, 'y': 0.0}
                    },
                    '_pivot': {
                        'id': 7,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 0.0, 'y': 0.0}
                    },
                    '_rotation': 0.0,
                    '_scale': {
                        'id': 8,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0}
                    },
                    '_groupID': -1,
                    '_sortingOrder': 1,
                    '_mapLevel': 0,
                    '_onTerrainLayer': False,
                    '_hidden': False,
                    '_locked': False,
                    '_superLocked': False,
                    '_hue': 0.5,
                    '_brightness': 0.5,
                    '_saturation': 0.5,
                    '_opacity': 1.0,
                    '_tint': {
                        'id': 9,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 0.9215686321258545, 'z': 0.01568627543747425}
                    },
                    '_flipH': False,
                    '_flipV': False,
                    '_ignoreTimeOfDay': False,
                    '_chromaKeyEnabled': False,
                    '_chromaKeyColour': {
                        'id': 10,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_chromeKeyTolerance': 0.07500000298023224,
                    '_lighting': {
                        'id': 11,
                        'class': 'TileLightingProperties',
                        'inline': False,
                        'members': {
                            '_hasLight': True,
                            '_lightRadius': {
                                'id': 12,
                                'class': 'System.Collections.Generic.List`1[[System.Single, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                                'inline': False,
                                'members': {
                                    '_items': {
                                        'id': 13,
                                        'array': [0, 11],
                                        'items': [2.56, 0.0, 0.0, 0.0]
                                    },
                                    '_size': 1,
                                    '_version': 1
                                }
                            },
                            '_lightR': 0.3409999907016754,
                            '_lightG': 0.3179999887943268,
                            '_lightB': 0.07100000232458115,
                            '_visibleThroughFog': False,
                            '_flicker': False,
                            '_darkness': False,
                            '_qualitySetting': 0,
                            '_fov': 360,
                            '_lightUpdates': True,
                            '_lightIntensity': 1.0,
                            '_lightDirection': 0
                        }
                    },
                    '_hasDropShadow': False,
                    '_blocksLight': False,
                    '_animation': {
                        'id': 14,
                        'class': 'TileAnimationProperties',
                        'inline': False,
                        'members': {
                            '_playing': True,
                            '_currentFrame': 0,
                            '_framesPerSecond': 30.0,
                            '_noOfFrames': 0.0,
                            '_triggered': False,
                            '_startFrame': 0.0,
                            '_endFrame': 0.0,
                            '_destroyAfterOnePlay': False,
                            '_delay': False,
                            '_delayTime': 0.0,
                            '_delayVariance': 0.0,
                            '_deactivateOnDelay': False,
                            '_ghostTileFrame': 0
                        }
                    },
                    '_effects': {
                        'id': 15,
                        'class': 'System.Collections.Generic.List`1[[IObjectEffect, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {
                            '_items': {
                                'id': 16,
                                'array': [
                                    4,
                                    {'name': 'IObjectEffect', 'library_id': 2}
                                ],
                                'items': []
                            },
                            '_size': 0,
                            '_version': 0
                        }
                    },
                    '_effectsNew': {
                        'id': 17,
                        'class': 'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {
                            '_items': {
                                'id': 18,
                                'array': [
                                    4,
                                    {'name': 'ObjectEffectBase', 'library_id': 2}
                                ],
                                'items': []
                            },
                            '_size': 0,
                            '_version': 0
                        }
                    },
                    '_alphaFriendlyCollider': False,
                    '_blocking': {
                        'id': 19,
                        'class': 'TileBlockingProperties',
                        'inline': False,
                        'members': {
                            '_blockingEnabled': False,
                            '_light': False,
                            '_vision': False,
                            '_sound': False,
                            '_movement': False,
                            '_oneWay': False,
                            '_oneWayDirection': False,
                            '_toggleable': False,
                            '_colliderMode': 0
                        }
                    },
                    '_chromaKeyReplacementColour': {
                        'id': 20,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_chromaKeyReplacementAlpha': 0.0,
                    '_uID': 1,
                    '_blockedByMovementBlockers': False,
                    '_dropShadow': {
                        'id': 21,
                        'class': 'TileDropShadowProperties',
                        'inline': False,
                        'members': {
                            '_shadowActive': True,
                            '_shadowStrengthUsesMapDefault': True,
                            '_shadowStrength': 1.0,
                            '_shadowSizeUsesMapDefault': True,
                            '_shadowSize': 1.0499999523162842,
                            '_shadowDistanceUsesMapDefault': True,
                            '_shadowDistance': 0.07500000298023224,
                            '_shadowDirectionUsesMapDefault': True,
                            '_shadowDirection': 1,
                            '_followsSunUsesMapDefault': True,
                            '_dropShadowsFollowSun': False
                        }
                    },
                    '_dropShadowLegacyUpgrade': True,
                    '_ambience': {
                        'id': 22,
                        'class': 'TileAmbienceProperties',
                        'inline': False,
                        'members': {
                            '_active': False,
                            '_audioPath': None,
                            '_radius': 12.799999237060547,
                            '_falloffRadius': 25.599998474121094,
                            '_volume': 1.0,
                            '_playWhenHidden': True,
                            '_activeTimeMin': 0.0,
                            '_activeTimeMax': 1.0,
                            '_playOnAllLevels': False
                        }
                    }
                }
            },
            '_placementType': {
                'id': 23,
                'class': 'MapOptions+ObjectPlacementType',
                'inline': True,
                'members': {'value__': 2}
            },
            '_brushType': {
                'id': 24,
                'class': 'MapOptions+PlacementType',
                'inline': True,
                'members': {'value__': 3}
            },
            '_gridType': {
                'id': 25,
                'class': 'MapOptions+GridType',
                'inline': True,
                'members': {'value__': 0}
            },
            'spriteWidth': 80.0,
            'spriteRatio': 1.0,
            '_trueSize': -1.0,
            '_additionalData': None
        }
    },
    'image': {
        'id': 1,
        'class': 'ArkenMapTileUpgradeBase',
        'inline': False,
        'members': {
            '_tileInfo': {
                'id': 2,
                'class': 'ArkenTilePresetBase',
                'inline': False,
                'members': {
                    '_name': 'Background',
                    '_baseName': None,
                    '_editable': True,
                    '_visibleInLibrary': True,
                    '_official': False,
                    '_imported': False,
                    '_version': 0,
                    '_tileName': 'Background',
                    '_tilePack': '',
                    '_tileCreator': '',
                    '_tilePath': 'MyAssets/Media/Generated/Background.rwmeta',
                    '_tileType': {
                        'id': 3,
                        'class': 'ArkenTile+TileType',
                        'inline': True,
                        'members': {'value__': 8}
                    },
                    '_category': {
                        'id': 4,
                        'class': 'ArkenTileUpgrade+TileCategory',
                        'inline': True,
                        'members': {'value__': 0}
                    },
                    '_defaultPlacementType': {
                        'id': 5,
                        'class': 'MapOptions+ObjectPlacementType',
                        'inline': True,
                        'members': {'value__': 2}
                    },
                    '_position': {
                        'id': 6,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 1.28, 'y': -1.28}
                    },
                    '_pivot': {
                        'id': 7,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 0.0, 'y': 0.0}
                    },
                    '_rotation': 0.0,
                    '_scale': {
                        'id': 8,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 2.56, 'y': 2.56}
                    },
                    '_groupID': -1,
                    '_sortingOrder': 0,
                    '_mapLevel': 0,
                    '_onTerrainLayer': False,
                    '_hidden': False,
                    '_locked': False,
                    '_superLocked': False,
                    '_hue': 0.5,
                    '_brightness': 0.5,
                    '_saturation': 0.5,
                    '_opacity': 1.0,
                    '_tint': {
                        'id': 9,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_flipH': False,
                    '_flipV': False,
                    '_ignoreTimeOfDay': False,
                    '_chromaKeyEnabled': False,
                    '_chromaKeyColour': {
                        'id': 10,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_chromeKeyTolerance': 0.07500000298023224,
                    '_lighting': {
                        'id': 11,
                        'class': 'TileLightingProperties',
                        'inline': False,
                        'members': {
                            '_hasLight': False,
                            '_lightRadius': {
                                'id': 12,
                                'class': 'System.Collections.Generic.List`1[[System.Single, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                                'inline': False,
                                'members': {
                                    '_items': {
                                        'id': 13,
                                        'array': [0, 11],
                                        'items': [12.799999237060547, 0.0, 0.0, 0.0]
                                    },
                                    '_size': 1,
                                    '_version': 1
                                }
                            },
                            '_lightR': 0.3409999907016754,
                            '_lightG': 0.3179999887943268,
                            '_lightB': 0.07100000232458115,
                            '_visibleThroughFog': False,
                            '_flicker': False,
                            '_darkness': False,
                            '_qualitySetting': 0,
                            '_fov': 360,
                            '_lightUpdates': True,
                            '_lightIntensity': 1.0,
                            '_lightDirection': 0
                        }
                    },
                    '_hasDropShadow': False,
                    '_blocksLight': False,
                    '_animation': {
                        'id': 14,
                        'class': 'TileAnimationProperties',
                        'inline': False,
                        'members': {
                            '_playing': True,
                            '_currentFrame': 0,
                            '_framesPerSecond': 30.0,
                            '_noOfFrames': 0.0,
                            '_triggered': False,
                            '_startFrame': 0.0,
                            '_endFrame': 0.0,
                            '_destroyAfterOnePlay': False,
                            '_delay': False,
                            '_delayTime': 0.0,
                            '_delayVariance': 0.0,
                            '_deactivateOnDelay': False,
                            '_ghostTileFrame': 0
                        }
                    },
                    '_effects': {
                        'id': 15,
                        'class': 'System.Collections.Generic.List`1[[IObjectEffect, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {
                            '_items': {
                                'id': 16,
                                'array': [
                                    4,
                                    {'name': 'IObjectEffect', 'library_id': 2}
                                ],
                                'items': []
                            },
                            '_size': 0,
                            '_version': 0
                        }
                    },
                    '_effectsNew': {
                        'id': 17,
                        'class': 'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {
                            '_items': {
                                'id': 18,
                                'array': [
                                    4,
                                    {'name': 'ObjectEffectBase', 'library_id': 2}
                                ],
                                'items': []
                            },
                            '_size': 0,
                            '_version': 0
                        }
                    },
                    '_alphaFriendlyCollider': False,
                    '_blocking': {
                        'id': 19,
                        'class': 'TileBlockingProperties',
                        'inline': False,
                        'members': {
                            '_blockingEnabled': False,
                            '_light': False,
                            '_vision': False,
                            '_sound': False,
                            '_movement': False,
                            '_oneWay': False,
                            '_oneWayDirection': False,
                            '_toggleable': False,
                            '_colliderMode': 2
                        }
                    },
                    '_chromaKeyReplacementColour': {
                        'id': 20,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_chromaKeyReplacementAlpha': 0.0,
                    '_uID': 1,
                    '_blockedByMovementBlockers': False,
                    '_dropShadow': {
                        'id': 21,
                        'class': 'TileDropShadowProperties',
                        'inline': False,
                        'members': {
                            '_shadowActive': True,
                            '_shadowStrengthUsesMapDefault': True,
                            '_shadowStrength': 1.0,
                            '_shadowSizeUsesMapDefault': True,
                            '_shadowSize': 1.0499999523162842,
                            '_shadowDistanceUsesMapDefault': True,
                            '_shadowDistance': 0.07500000298023224,
                            '_shadowDirectionUsesMapDefault': True,
                            '_shadowDirection': 1,
                            '_followsSunUsesMapDefault': True,
                            '_dropShadowsFollowSun': False
                        }
                    },
                    '_dropShadowLegacyUpgrade': True,
                    '_ambience': {
                        'id': 22,
                        'class': 'TileAmbienceProperties',
                        'inline': False,
                        'members': {
                            '_active': False,
                            '_audioPath': None,
                            '_radius': 12.799999237060547,
                            '_falloffRadius': 25.599998474121094,
                            '_volume': 1.0,
                            '_playWhenHidden': True,
                            '_activeTimeMin': 0.0,
                            '_activeTimeMax': 1.0,
                            '_playOnAllLevels': False
                        }
                    }
                }
            },
            '_placementType': {
                'id': 23,
                'class': 'MapOptions+ObjectPlacementType',
                'inline': True,
                'members': {'value__': 2}
            },
            '_brushType': {
                'id': 24,
                'class': 'MapOptions+PlacementType',
                'inline': True,
                'members': {'value__': 3}
            },
            '_gridType': {
                'id': 25,
                'class': 'MapOptions+GridType',
                'inline': True,
                'members': {'value__': 0}
            },
            'spriteWidth': 100.0,
            'spriteRatio': 1.0,
            '_trueSize': -1.0,
            '_additionalData': None
        }
    },
    'asset': {
        'id': 1,
        'class': 'ArkenTileUpgrade',
        'inline': False,
        'members': {
            '_name': 'Background',
            '_pack': '',
            '_creator': '',
            '_category': {
                'id': 2,
                'class': 'ArkenTileUpgrade+TileCategory',
                'inline': True,
                'members': {'value__': 0}
            },
            '_legacyType': {
                'id': 3,
                'class': 'ArkenTile+TileType',
                'inline': True,
                'members': {'value__': 8}
            },
            '_thumbnail': {
                'id': 4,
                'class': 'ArkenImage',
                'inline': False,
                'members': {
                    '_packImgX': -1,
                    '_packImgY': -1,
                    '_packImgChannels': 4,
                    '_packImageRAW': {'id': 5, 'bytes': 'generated PNG'}
                }
            },
            '_thumbnailScale': 0.030476190149784088,
            '_content': {
                'id': 6,
                'class': 'ArkenImage',
                'inline': False,
                'members': {
                    '_packImgX': -1,
                    '_packImgY': -1,
                    '_packImgChannels': 4,
                    '_packImageRAW': {'use': 5}
                }
            }
        }
    },
    'asset_meta': {
        'id': 1,
        'class': 'ArkenTileMeta',
        'inline': False,
        'members': {
            '_category': None,
            '_tileType': {
                'id': 2,
                'class': 'ArkenTile+TileType',
                'inline': True,
                'members': {'value__': 8}
            },
            '_tileCategory': {
                'id': 3,
                'class': 'ArkenTileUpgrade+TileCategory',
                'inline': True,
                'members': {'value__': 0}
            },
            '_thumbnail': {
                'id': 4,
                'class': 'ArkenImage',
                'inline': False,
                'members': {
                    '_packImgX': -1,
                    '_packImgY': -1,
                    '_packImgChannels': 4,
                    '_packImageRAW': {'id': 5, 'bytes': 'generated PNG'}
                }
            },
            '_thumbnailScale': 0.030476190149784088,
            '_variations': {
                'id': 6,
                'class': 'System.Collections.Generic.List`1[[ArkenTilePresetBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                'inline': False,
                'members': {
                    '_items': {
                        'id': 7,
                        'array': [
                            4,
                            {'name': 'ArkenTilePresetBase', 'library_id': 2}
                        ],
                        'items': [
                            {
                                'id': 8,
                                'class': 'ArkenTilePresetBase',
                                'inline': False,
                                'members': {
                                    '_name': 'Background',
                                    '_baseName': None,
                                    '_editable': True,
                                    '_visibleInLibrary': True,
                                    '_official': False,
                                    '_imported': False,
                                    '_version': 0,
                                    '_tileName': 'Background',
                                    '_tilePack': '',
                                    '_tileCreator': '',
                                    '_tilePath': None,
                                    '_tileType': {
                                        'id': 9,
                                        'class': 'ArkenTile+TileType',
                                        'inline': True,
                                        'members': {'value__': 8}
                                    },
                                    '_category': {
                                        'id': 10,
                                        'class': 'ArkenTileUpgrade+TileCategory',
                                        'inline': True,
                                        'members': {'value__': 0}
                                    },
                                    '_defaultPlacementType': {
                                        'id': 11,
                                        'class': 'MapOptions+ObjectPlacementType',
                                        'inline': True,
                                        'members': {'value__': 2}
                                    },
                                    '_position': {
                                        'id': 12,
                                        'class': 'SVector2',
                                        'inline': False,
                                        'members': {'x': 0.0, 'y': 0.0}
                                    },
                                    '_pivot': {
                                        'id': 13,
                                        'class': 'SVector2',
                                        'inline': False,
                                        'members': {'x': 0.0, 'y': 0.0}
                                    },
                                    '_rotation': 0.0,
                                    '_scale': {
                                        'id': 14,
                                        'class': 'SVector2',
                                        'inline': False,
                                        'members': {'x': 2.559999942779541, 'y': 2.559999942779541}
                                    },
                                    '_groupID': -1,
                                    '_sortingOrder': -1,
                                    '_mapLevel': 0,
                                    '_onTerrainLayer': False,
                                    '_hidden': False,
                                    '_locked': False,
                                    '_superLocked': False,
                                    '_hue': 0.5,
                                    '_brightness': 0.5,
                                    '_saturation': 0.5,
                                    '_opacity': 1.0,
                                    '_tint': {
                                        'id': 15,
                                        'class': 'SVector3',
                                        'inline': False,
                                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                                    },
                                    '_flipH': False,
                                    '_flipV': False,
                                    '_ignoreTimeOfDay': False,
                                    '_chromaKeyEnabled': False,
                                    '_chromaKeyColour': {
                                        'id': 16,
                                        'class': 'SVector3',
                                        'inline': False,
                                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                                    },
                                    '_chromeKeyTolerance': 0.07500000298023224,
                                    '_lighting': {
                                        'id': 17,
                                        'class': 'TileLightingProperties',
                                        'inline': False,
                                        'members': {
                                            '_hasLight': False,
                                            '_lightRadius': {
                                                'id': 18,
                                                'class': 'System.Collections.Generic.List`1[[System.Single, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                                                'inline': False,
                                                'members': {
                                                    '_items': {
                                                        'id': 19,
                                                        'array': [0, 11],
                                                        'items': [12.799999237060547, 0.0, 0.0, 0.0]
                                                    },
                                                    '_size': 1,
                                                    '_version': 1
                                                }
                                            },
                                            '_lightR': 0.3409999907016754,
                                            '_lightG': 0.3179999887943268,
                                            '_lightB': 0.07100000232458115,
                                            '_visibleThroughFog': False,
                                            '_flicker': False,
                                            '_darkness': False,
                                            '_qualitySetting': 0,
                                            '_fov': 360,
                                            '_lightUpdates': True,
                                            '_lightIntensity': 1.0,
                                            '_lightDirection': 0
                                        }
                                    },
                                    '_hasDropShadow': False,
                                    '_blocksLight': False,
                                    '_animation': {
                                        'id': 20,
                                        'class': 'TileAnimationProperties',
                                        'inline': False,
                                        'members': {
                                            '_playing': True,
                                            '_currentFrame': 0,
                                            '_framesPerSecond': 30.0,
                                            '_noOfFrames': 0.0,
                                            '_triggered': False,
                                            '_startFrame': 0.0,
                                            '_endFrame': 0.0,
                                            '_destroyAfterOnePlay': False,
                                            '_delay': False,
                                            '_delayTime': 0.0,
                                            '_delayVariance': 0.0,
                                            '_deactivateOnDelay': False,
                                            '_ghostTileFrame': 0
                                        }
                                    },
                                    '_effects': {
                                        'id': 21,
                                        'class': 'System.Collections.Generic.List`1[[IObjectEffect, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                                        'inline': False,
                                        'members': {
                                            '_items': {
                                                'id': 22,
                                                'array': [
                                                    4,
                                                    {'name': 'IObjectEffect', 'library_id': 2}
                                                ],
                                                'items': []
                                            },
                                            '_size': 0,
                                            '_version': 0
                                        }
                                    },
                                    '_effectsNew': {
                                        'id': 23,
                                        'class': 'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                                        'inline': False,
                                        'members': {
                                            '_items': {
                                                'id': 24,
                                                'array': [
                                                    4,
                                                    {'name': 'ObjectEffectBase', 'library_id': 2}
                                                ],
                                                'items': []
                                            },
                                            '_size': 0,
                                            '_version': 0
                                        }
                                    },
                                    '_alphaFriendlyCollider': False,
                                    '_blocking': {
                                        'id': 25,
                                        'class': 'TileBlockingProperties',
                                        'inline': False,
                                        'members': {
                                            '_blockingEnabled': False,
                                            '_light': False,
                                            '_vision': False,
                                            '_sound': False,
                                            '_movement': False,
                                            '_oneWay': False,
                                            '_oneWayDirection': False,
                                            '_toggleable': False,
                                            '_colliderMode': 2
                                        }
                                    },
                                    '_chromaKeyReplacementColour': {
                                        'id': 26,
                                        'class': 'SVector3',
                                        'inline': False,
                                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                                    },
                                    '_chromaKeyReplacementAlpha': 0.0,
                                    '_uID': -1,
                                    '_blockedByMovementBlockers': False,
                                    '_dropShadow': {
                                        'id': 27,
                                        'class': 'TileDropShadowProperties',
                                        'inline': False,
                                        'members': {
                                            '_shadowActive': True,
                                            '_shadowStrengthUsesMapDefault': True,
                                            '_shadowStrength': 1.0,
                                            '_shadowSizeUsesMapDefault': True,
                                            '_shadowSize': 1.0499999523162842,
                                            '_shadowDistanceUsesMapDefault': True,
                                            '_shadowDistance': 0.07500000298023224,
                                            '_shadowDirectionUsesMapDefault': True,
                                            '_shadowDirection': 1,
                                            '_followsSunUsesMapDefault': True,
                                            '_dropShadowsFollowSun': False
                                        }
                                    },
                                    '_dropShadowLegacyUpgrade': True,
                                    '_ambience': {
                                        'id': 28,
                                        'class': 'TileAmbienceProperties',
                                        'inline': False,
                                        'members': {
                                            '_active': False,
                                            '_audioPath': None,
                                            '_radius': 12.799999237060547,
                                            '_falloffRadius': 25.599998474121094,
                                            '_volume': 1.0,
                                            '_playWhenHidden': True,
                                            '_activeTimeMin': 0.0,
                                            '_activeTimeMax': 1.0,
                                            '_playOnAllLevels': False
                                        }
                                    }
                                }
                            },
                            None,
                            None,
                            None
                        ]
                    },
                    '_size': 1,
                    '_version': 1
                }
            },
            '_name': 'Background',
            '_pack': '',
            '_creator': '',
            '_genre': '',
            '_subgenre': '',
            '_tags': {
                'id': 29,
                'class': 'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                'inline': False,
                'members': {
                    '_items': {
                        'id': 30,
                        'array': [1, None],
                        'items': []
                    },
                    '_size': 0,
                    '_version': 0
                }
            },
            '_starred': False,
            '_hideFromView': False,
            '_includedWorldPaths': None,
            '_official': False,
            '_prevPathIfDeleted': None,
            '_links': {
                'id': 31,
                'class': 'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                'inline': False,
                'members': {
                    '_items': {'use': 30},
                    '_size': 0,
                    '_version': 0
                }
            },
            'ArkenBaseMeta+_name': 'Background',
            'ArkenBaseMeta+_pack': '',
            'ArkenBaseMeta+_creator': '',
            'ArkenBaseMeta+_genre': '',
            'ArkenBaseMeta+_subgenre': '',
            'ArkenBaseMeta+_tags': {'use': 29},
            'ArkenBaseMeta+_starred': False,
            'ArkenBaseMeta+_hideFromView': False,
            'ArkenBaseMeta+_includedWorldPaths': None,
            'ArkenBaseMeta+_official': False,
            'ArkenBaseMeta+_prevPathIfDeleted': None,
            'ArkenBaseMeta+_links': {'use': 31},
            'LinkableContent+_links': {'use': 31}
        }
    },
    'blank': {
        'id': 1,
        'class': 'ArkenMapUpgrade',
        'inline': False,
        'members': {
            '_name': 'Generated Geometry',
            '_pack': None,
            '_packCreator': None,
            '_lastModifiedDate': '134116992000000000',
            '_creator': 'ForgeBridge',
            '_creationDate': '134116992000000000',
            '_description': None,
            '_canBeCommercialized': False,
            '_tiles': {
                'id': 2,
                'class': 'System.Collections.Generic.List`1[[ArkenMapTileUpgradeBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                'inline': False,
                'members': {
                    '_items': {
                        'id': 3,
                        'array': [
                            4,
                            {'name': 'ArkenMapTileUpgradeBase', 'library_id': 2}
                        ],
                        'items': []
                    },
                    '_size': 0,
                    '_version': 0
                }
            },
            '_timeOfDay': 0.5,
            '_dropShadow': {
                'id': 4,
                'class': 'MapDropShadowProperties',
                'inline': False,
                'members': {
                    '_dropShadowDirection': 215,
                    '_dropShadowSize': 1.0499999523162842,
                    '_dropShadowDistance': 0.07500000298023224,
                    '_dropShadowStrength': 0.36000001430511475,
                    '_dropShadowFollowsSun': True,
                    '_dropShadowFollowsSunNorthernHemisphere': True,
                    '_dropShadowsEnabled': True
                }
            },
            '_linkedPresets': {
                'id': 5,
                'array': [
                    4,
                    {'name': 'SoundscapePreset', 'library_id': 2}
                ],
                'items': [None, None, None]
            },
            '_bookmarks': {
                'id': 6,
                'class': 'System.Collections.Generic.List`1[[MapBookmark, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                'inline': False,
                'members': {
                    '_items': {
                        'id': 7,
                        'array': [
                            4,
                            {'name': 'MapBookmark', 'library_id': 2}
                        ],
                        'items': []
                    },
                    '_size': 0,
                    '_version': 0
                }
            },
            '_fogLevelDataFull': {
                'id': 8,
                'class': 'System.Collections.Generic.Dictionary`2[[System.Int32, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089],[System.Collections.Generic.List`1[[FoW.FogOfWarChunk, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]], mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                'inline': False,
                'members': {
                    'Version': 0,
                    'Comparer': {
                        'id': 9,
                        'class': 'System.Collections.Generic.GenericEqualityComparer`1[[System.Int32, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                        'inline': False,
                        'members': {}
                    },
                    'HashSize': 0
                }
            },
            '_gridType': {
                'id': 10,
                'class': 'MapOptions+GridType',
                'inline': True,
                'members': {'value__': 0}
            },
            '_gridDisplay': {
                'id': 11,
                'class': 'MapOptions+GridDisplay',
                'inline': True,
                'members': {'value__': 0}
            },
            '_gridTransparency': 0.5,
            '_gridColourR': 0.0,
            '_gridColourG': 0.0,
            '_gridColourB': 0.0,
            '_gridBelowObjects': True,
            '_backgroundColour': {
                'id': 12,
                'class': 'SVector3',
                'inline': False,
                'members': {'x': 0.1568627506494522, 'y': 0.1568627506494522, 'z': 0.1568627506494522}
            },
            '_fogEnabled': True,
            '_fogMode': {
                'id': 13,
                'class': 'FogOfWarOptions+FogMode',
                'inline': True,
                'members': {'value__': 1}
            },
            '_fogPersists': True,
            '_fogColour': None,
            '_mapRotation': 0.0,
            '_embeddedLinks': {
                'id': 14,
                'class': 'System.Collections.Generic.List`1[[EmbeddedLink, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                'inline': False,
                'members': {
                    '_items': {
                        'id': 15,
                        'array': [
                            4,
                            {'name': 'EmbeddedLink', 'library_id': 2}
                        ],
                        'items': []
                    },
                    '_size': 0,
                    '_version': 0
                }
            },
            '_layersInOrder': False,
            '_importedTiles': {
                'id': 16,
                'class': 'System.Collections.Generic.Dictionary`2[[ArkenTileUpgrade, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null],[System.Collections.Generic.List`1[[ArkenTilePresetBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]], mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                'inline': False,
                'members': {
                    'Version': 0,
                    'Comparer': {
                        'id': 17,
                        'class': 'System.Collections.Generic.ObjectEqualityComparer`1[[ArkenTileUpgrade, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {}
                    },
                    'HashSize': 0
                }
            },
            '_useCustomAmbienceColour': False,
            '_customAmbientColour': {
                'id': 18,
                'class': 'SVector3',
                'inline': False,
                'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
            },
            '_useCustomLightIntensity': False,
            '_customLightIntensity': 0.5,
            '_multilevelMap': False,
            '_playerScreenLocation': None,
            '_playerScreenSize': 0.0,
            '_nextUID': 0,
            '_gridEnabled': True,
            '_playerMapFollowUID': -1,
            '_playerSplashScreen': None,
            '_startPointSetManually': False,
            '_mapRotationPlayer': 0.0,
            '_playerMapFollowObject': False,
            '_mapBackgroundTexture': 'Grass1'
        }
    },
    'map_meta': {
        'id': 1,
        'class': 'ArkenMapMeta',
        'inline': False,
        'members': {
            '_mapName': 'Generated Map',
            '_mapCreator': 'ForgeBridge',
            '_mapType': {
                'id': 2,
                'class': 'MapOptions+MapModule',
                'inline': True,
                'members': {'value__': 0}
            },
            '_creationDate': '1/1/2026',
            '_lastModified': '134116992000000000',
            '_description': None,
            '_canBeCommercialized': False,
            '_favourited': False,
            '_isAutosave': False,
            '_autosavePath': None,
            '_thumbnail': None,
            '_bookmarks': {
                'id': 3,
                'class': 'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                'inline': False,
                'members': {
                    '_items': {
                        'id': 4,
                        'array': [1, None],
                        'items': []
                    },
                    '_size': 0,
                    '_version': 0
                }
            },
            '_name': 'Generated Map',
            '_pack': '',
            '_creator': '',
            '_genre': '',
            '_subgenre': '',
            '_tags': {
                'id': 5,
                'class': 'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                'inline': False,
                'members': {
                    '_items': {'use': 4},
                    '_size': 0,
                    '_version': 0
                }
            },
            '_starred': False,
            '_hideFromView': False,
            '_includedWorldPaths': None,
            '_official': False,
            '_prevPathIfDeleted': None,
            '_links': {
                'id': 6,
                'class': 'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                'inline': False,
                'members': {
                    '_items': {'use': 4},
                    '_size': 0,
                    '_version': 0
                }
            },
            'ArkenBaseMeta+_name': 'Generated Map',
            'ArkenBaseMeta+_pack': '',
            'ArkenBaseMeta+_creator': '',
            'ArkenBaseMeta+_genre': '',
            'ArkenBaseMeta+_subgenre': '',
            'ArkenBaseMeta+_tags': {'use': 5},
            'ArkenBaseMeta+_starred': False,
            'ArkenBaseMeta+_hideFromView': False,
            'ArkenBaseMeta+_includedWorldPaths': None,
            'ArkenBaseMeta+_official': False,
            'ArkenBaseMeta+_prevPathIfDeleted': None,
            'ArkenBaseMeta+_links': {'use': 6},
            'LinkableContent+_links': {'use': 6}
        }
    },
    'content': {
        'id': 1,
        'class': 'ArkenMapTileUpgradeBase',
        'inline': False,
        'members': {
            '_tileInfo': {
                'id': 2,
                'class': 'ArkenTilePresetContentLink',
                'inline': False,
                'members': {
                    '_contentBasePath': 'MyAssets/Encyclopedia/Notes/GeneratedControls/Control.rwmeta',
                    '_contentType': 'note',
                    '_onlyShowOnMyLevel': False,
                    '_useDefaultTint': False,
                    '_visibleOnLowerLevels': True,
                    '_name': 'ForgeBridge Control',
                    '_editable': True,
                    '_visibleInLibrary': True,
                    '_official': False,
                    '_imported': False,
                    '_version': 0,
                    '_tileName': 'ForgeBridge Control',
                    '_tilePack': '',
                    '_tileCreator': '',
                    '_tilePath': None,
                    '_tileType': {
                        'id': 3,
                        'class': 'ArkenTile+TileType',
                        'inline': True,
                        'members': {'value__': 8}
                    },
                    '_category': {
                        'id': 4,
                        'class': 'ArkenTileUpgrade+TileCategory',
                        'inline': True,
                        'members': {'value__': 0}
                    },
                    '_defaultPlacementType': {
                        'id': 5,
                        'class': 'MapOptions+ObjectPlacementType',
                        'inline': True,
                        'members': {'value__': 2}
                    },
                    '_position': {
                        'id': 6,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 0.0, 'y': 0.0}
                    },
                    '_pivot': {
                        'id': 7,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 0.0, 'y': 0.0}
                    },
                    '_rotation': 0.0,
                    '_scale': {
                        'id': 8,
                        'class': 'SVector2',
                        'inline': False,
                        'members': {'x': 0.512, 'y': 0.512}
                    },
                    '_groupID': -1,
                    '_sortingOrder': 1,
                    '_mapLevel': 0,
                    '_onTerrainLayer': False,
                    '_hidden': False,
                    '_locked': False,
                    '_superLocked': False,
                    '_hue': 0.5,
                    '_brightness': 0.5,
                    '_saturation': 0.5,
                    '_opacity': 1.0,
                    '_tint': {
                        'id': 9,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_flipH': False,
                    '_flipV': False,
                    '_ignoreTimeOfDay': False,
                    '_chromaKeyEnabled': False,
                    '_chromaKeyColour': {
                        'id': 10,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_chromeKeyTolerance': 0.07500000298023224,
                    '_lighting': {
                        'id': 11,
                        'class': 'TileLightingProperties',
                        'inline': False,
                        'members': {
                            '_hasLight': False,
                            '_lightRadius': {
                                'id': 12,
                                'class': 'System.Collections.Generic.List`1[[System.Single, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                                'inline': False,
                                'members': {
                                    '_items': {
                                        'id': 13,
                                        'array': [0, 11],
                                        'items': [12.799999237060547, 0.0, 0.0, 0.0]
                                    },
                                    '_size': 1,
                                    '_version': 1
                                }
                            },
                            '_lightR': 0.3409999907016754,
                            '_lightG': 0.3179999887943268,
                            '_lightB': 0.07100000232458115,
                            '_visibleThroughFog': False,
                            '_flicker': False,
                            '_darkness': False,
                            '_qualitySetting': 0,
                            '_fov': 360,
                            '_lightUpdates': True,
                            '_lightIntensity': 1.0,
                            '_lightDirection': 0
                        }
                    },
                    '_hasDropShadow': False,
                    '_blocksLight': False,
                    '_animation': {
                        'id': 14,
                        'class': 'TileAnimationProperties',
                        'inline': False,
                        'members': {
                            '_playing': True,
                            '_currentFrame': 0,
                            '_framesPerSecond': 30.0,
                            '_noOfFrames': 0.0,
                            '_triggered': False,
                            '_startFrame': 0.0,
                            '_endFrame': 0.0,
                            '_destroyAfterOnePlay': False,
                            '_delay': False,
                            '_delayTime': 0.0,
                            '_delayVariance': 0.0,
                            '_deactivateOnDelay': False,
                            '_ghostTileFrame': 0
                        }
                    },
                    '_effectsNew': {
                        'id': 15,
                        'class': 'System.Collections.Generic.List`1[[ObjectEffectBase, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {
                            '_items': {
                                'id': 16,
                                'array': [
                                    4,
                                    {'name': 'ObjectEffectBase', 'library_id': 2}
                                ],
                                'items': []
                            },
                            '_size': 0,
                            '_version': 0
                        }
                    },
                    '_alphaFriendlyCollider': False,
                    '_blocking': {
                        'id': 17,
                        'class': 'TileBlockingProperties',
                        'inline': False,
                        'members': {
                            '_blockingEnabled': False,
                            '_light': False,
                            '_vision': False,
                            '_sound': False,
                            '_movement': False,
                            '_oneWay': False,
                            '_oneWayDirection': False,
                            '_toggleable': False,
                            '_colliderMode': 0
                        }
                    },
                    '_chromaKeyReplacementColour': {
                        'id': 18,
                        'class': 'SVector3',
                        'inline': False,
                        'members': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                    },
                    '_chromaKeyReplacementAlpha': 0.0,
                    '_uID': 1,
                    '_blockedByMovementBlockers': False,
                    'ArkenTilePresetBase+_name': 'ForgeBridge Control',
                    'ArkenTilePresetBase+_baseName': None,
                    'ArkenTilePresetBase+_editable': True,
                    'ArkenTilePresetBase+_visibleInLibrary': True,
                    'ArkenTilePresetBase+_official': False,
                    'ArkenTilePresetBase+_imported': False,
                    'ArkenTilePresetBase+_version': 0,
                    'ArkenTilePresetBase+_tileName': 'ForgeBridge Control',
                    'ArkenTilePresetBase+_tilePack': '',
                    'ArkenTilePresetBase+_tileCreator': '',
                    'ArkenTilePresetBase+_tilePath': None,
                    'ArkenTilePresetBase+_tileType': {
                        'id': 19,
                        'class': 'ArkenTile+TileType',
                        'inline': True,
                        'members': {'value__': 8}
                    },
                    'ArkenTilePresetBase+_category': {
                        'id': 20,
                        'class': 'ArkenTileUpgrade+TileCategory',
                        'inline': True,
                        'members': {'value__': 0}
                    },
                    'ArkenTilePresetBase+_defaultPlacementType': {
                        'id': 21,
                        'class': 'MapOptions+ObjectPlacementType',
                        'inline': True,
                        'members': {'value__': 2}
                    },
                    'ArkenTilePresetBase+_position': {'use': 6},
                    'ArkenTilePresetBase+_pivot': {'use': 7},
                    'ArkenTilePresetBase+_rotation': 0.0,
                    'ArkenTilePresetBase+_scale': {'use': 8},
                    'ArkenTilePresetBase+_groupID': -1,
                    'ArkenTilePresetBase+_sortingOrder': 1,
                    'ArkenTilePresetBase+_mapLevel': 0,
                    'ArkenTilePresetBase+_onTerrainLayer': False,
                    'ArkenTilePresetBase+_hidden': False,
                    'ArkenTilePresetBase+_locked': False,
                    'ArkenTilePresetBase+_superLocked': False,
                    'ArkenTilePresetBase+_hue': 0.5,
                    'ArkenTilePresetBase+_brightness': 0.5,
                    'ArkenTilePresetBase+_saturation': 0.5,
                    'ArkenTilePresetBase+_opacity': 1.0,
                    'ArkenTilePresetBase+_tint': {'use': 9},
                    'ArkenTilePresetBase+_flipH': False,
                    'ArkenTilePresetBase+_flipV': False,
                    'ArkenTilePresetBase+_ignoreTimeOfDay': False,
                    'ArkenTilePresetBase+_chromaKeyEnabled': False,
                    'ArkenTilePresetBase+_chromaKeyColour': {'use': 10},
                    'ArkenTilePresetBase+_chromeKeyTolerance': 0.07500000298023224,
                    'ArkenTilePresetBase+_lighting': {'use': 11},
                    'ArkenTilePresetBase+_hasDropShadow': False,
                    'ArkenTilePresetBase+_blocksLight': False,
                    'ArkenTilePresetBase+_animation': {'use': 14},
                    'ArkenTilePresetBase+_effects': {
                        'id': 22,
                        'class': 'System.Collections.Generic.List`1[[IObjectEffect, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]',
                        'inline': False,
                        'members': {
                            '_items': {
                                'id': 23,
                                'array': [
                                    4,
                                    {'name': 'IObjectEffect', 'library_id': 2}
                                ],
                                'items': []
                            },
                            '_size': 0,
                            '_version': 0
                        }
                    },
                    'ArkenTilePresetBase+_effectsNew': {'use': 15},
                    'ArkenTilePresetBase+_alphaFriendlyCollider': False,
                    'ArkenTilePresetBase+_blocking': {'use': 17},
                    'ArkenTilePresetBase+_chromaKeyReplacementColour': {'use': 18},
                    'ArkenTilePresetBase+_chromaKeyReplacementAlpha': 0.0,
                    'ArkenTilePresetBase+_uID': 1,
                    'ArkenTilePresetBase+_blockedByMovementBlockers': False,
                    'ArkenTilePresetBase+_dropShadow': {
                        'id': 24,
                        'class': 'TileDropShadowProperties',
                        'inline': False,
                        'members': {
                            '_shadowActive': True,
                            '_shadowStrengthUsesMapDefault': True,
                            '_shadowStrength': 1.0,
                            '_shadowSizeUsesMapDefault': True,
                            '_shadowSize': 1.0499999523162842,
                            '_shadowDistanceUsesMapDefault': True,
                            '_shadowDistance': 0.07500000298023224,
                            '_shadowDirectionUsesMapDefault': True,
                            '_shadowDirection': 1,
                            '_followsSunUsesMapDefault': True,
                            '_dropShadowsFollowSun': False
                        }
                    },
                    'ArkenTilePresetBase+_dropShadowLegacyUpgrade': True,
                    'ArkenTilePresetBase+_ambience': {
                        'id': 25,
                        'class': 'TileAmbienceProperties',
                        'inline': False,
                        'members': {
                            '_active': False,
                            '_audioPath': None,
                            '_radius': 12.799999237060547,
                            '_falloffRadius': 25.599998474121094,
                            '_volume': 1.0,
                            '_playWhenHidden': True,
                            '_activeTimeMin': 0.0,
                            '_activeTimeMax': 1.0,
                            '_playOnAllLevels': False
                        }
                    }
                }
            },
            '_placementType': {
                'id': 26,
                'class': 'MapOptions+ObjectPlacementType',
                'inline': True,
                'members': {'value__': 14}
            },
            '_brushType': {
                'id': 27,
                'class': 'MapOptions+PlacementType',
                'inline': True,
                'members': {'value__': 3}
            },
            '_gridType': {
                'id': 28,
                'class': 'MapOptions+GridType',
                'inline': True,
                'members': {'value__': 0}
            },
            'spriteWidth': 512.0,
            'spriteRatio': 1.0,
            '_trueSize': -1.0,
            '_additionalData': None
        }
    },
    'size': {
        'id': 1,
        'class': 'ArkenNoteFieldSize',
        'inline': False,
        'members': {
            '_squareSize': -1,
            '_squareSizeNew': 1.0,
            '_headingColour': {
                'id': 2,
                'class': 'SVector3',
                'inline': False,
                'members': {'x': 90.0, 'y': 90.0, 'z': 90.0}
            },
            '_name': 'Size',
            '_visibleToPlayers': {
                'id': 3,
                'class': 'System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]',
                'inline': False,
                'members': {
                    '_items': {
                        'id': 4,
                        'array': [1, None],
                        'items': []
                    },
                    '_size': 0,
                    '_version': 0
                }
            },
            '_UID': 1,
            'ArkenNoteField+_name': 'Size',
            'ArkenNoteField+_visibleToPlayers': {'use': 3},
            'ArkenNoteField+_UID': 1
        }
    }
}

$(function () {
    'use strict'

    /* Settings. */
	const showSearchMarker = true // Show a marker on the map's scan location. Default: false.
    const isSearchMarkerMovable = false // Let the user move the scan location marker around. Doesn't do anything without --no-fixed-location. Default: false.
    const showLocationMarker = true // Show a marker on the visitor's location. Default: false.
    const isLocationMarkerMovable = false // Let the user move the visitor marker around. Default: false.
	
    const scaleByRarity = true // Enable scaling by rarity. Default: true.
    const upscalePokemon = false // Enable upscaling of certain Pokemon (upscaledPokemon and notify list). Default: false.
    const upscaledPokemon = [] // Add Pokémon IDs separated by commas (e.g. [1, 2, 3]) to upscale icons. Default: [].

    // Google Analytics property ID. Leave empty to disable.
    // Looks like 'UA-XXXXX-Y'.
    const analyticsKey = ''

    // Hide Presets

    const hidepresets= [
     {
       PokemonID: 149,
       Name: "only Dragon",
       Searchstring: ['Dragon'],
       Invert: true
     },
     {
       PokemonID: 230,
       Name: "only Water",
       Searchstring: ['Water'],
       Invert: true
     },
     {
       PokemonID: 208,
       Name: "only Steel",
       Searchstring: ['Steel'],
       Invert: true
     },
     {
       PokemonID: 25,
       Name: "only Electric",
       Searchstring: ['Electric'],
       Invert: true
     },
     {
       PokemonID: 4,
       Name: "only Fire",
       Searchstring: ['Fire'],
       Invert: true
     },
     {
       PokemonID: 198,
       Name: "only Dark",
       Searchstring: ['Dark'],
       Invert: true
     },
     {
       PokemonID: 10,
       Name: "only Bug",
       Searchstring: ['Bug'],
       Invert: true
     },
     {
       PokemonID: 16,
       Name: "only Normal",
       Searchstring: ['Normal'],
       Invert: true
     },
     {
       PokemonID: 66,
       Name: "only Fight",
       Searchstring: ['Fighting'],
       Invert: true
     },
     {
       PokemonID: 92,
       Name: "only Ghost",
       Searchstring: ['Ghost'],
       Invert: true
     },
     {
       PokemonID: 63,
       Name: "only Psychic",
       Searchstring: ['Psychic'],
       Invert: true
     },
     {
       PokemonID: 12,
       Name: "only Flying",
       Searchstring: ['Flying'],
       Invert: true
     },
     {
       PokemonID: 1,
       Name: "only Grass",
       Searchstring: ['Grass'],
       Invert: true
     },
     {
       PokemonID: 29,
       Name: "only Poison",
       Searchstring: ['Poison'],
       Invert: true
     },
     {
       PokemonID: 35,
       Name: "only Fairy",
       Searchstring: ['Fairy'],
       Invert: true
     },
     {
       PokemonID: 364,
       Name: "only Ice",
       Searchstring: ['Ice'],
       Invert: true
     },
     {
       PokemonID: 1,
       Name: "Generation 1",
       Searchstring: ['gen1'],
       Invert: true
     },
     {
       PokemonID: 152,
       Name: "Generation 2",
       Searchstring: ['gen2'],
       Invert: true
     },
     {
       PokemonID: 252,
       Name: "Generation 3",
       Searchstring: ['gen3'],
       Invert: true
     }
    ]


    // MOTD.
    const motdEnabled = false
    const motdTitle = 'MOTD'
    const motd = 'Hi there! This is an easily customizable MOTD with optional title!'

    // Only show every unique MOTD message once. If disabled, the MOTD will be
    // shown on every visit. Requires support for localStorage.
    // Updating only the MOTD title (and not the text) will not make the MOTD
    // appear again.
    const motdShowOnlyOnce = true

    // What pages should the MOTD be shown on? By default, homepage and mobile
    // pages.
    const motdShowOnPages = [
        '/',
        '/mobile'
    ]

    // Clustering! Different zoom levels for desktop vs mobile.
    const disableClusters = false // Default: false.
    const maxClusterZoomLevel = 14 // Default: 14.
    const maxClusterZoomLevelMobile = 14 // Default: 14.
    const clusterZoomOnClick = false // Default: false.
    const clusterZoomOnClickMobile = false // Default: 14.
    const clusterGridSize = 60 // Default: 60.
    const clusterGridSizeMobile = 60 // Default: 60.

    // Process Pokémon in chunks to improve responsiveness.
    const processPokemonChunkSize = 100 // Default: 100
    const processPokemonIntervalMs = 100 // Default: 100ms
	const processPokemonChunkSizeMobile = 100 // Default: 100.
	const processPokemonIntervalMsMobile = 100 // Default: 100ms.

    /* Feature detection. */

    const hasStorage = (function () {
        var mod = 'RocketMap'
        try {
            localStorage.setItem(mod, mod)
            localStorage.removeItem(mod)
            return true
        } catch (exception) {
            return false
        }
    }())


    /* Do stuff. */

    const currentPage = window.location.pathname
	// Marker cluster might have loaded before custom.js.
    const isMarkerClusterLoaded = typeof window.markerCluster !== 'undefined' && !!window.markerCluster

    // Set custom Store values.
    Store.set('maxClusterZoomLevel', maxClusterZoomLevel)
    Store.set('clusterZoomOnClick', clusterZoomOnClick)
    Store.set('clusterGridSize', clusterGridSize)
    Store.set('processPokemonChunkSize', processPokemonChunkSize)
    Store.set('processPokemonIntervalMs', processPokemonIntervalMs)
    Store.set('scaleByRarity', scaleByRarity)
    Store.set('upscalePokemon', upscalePokemon)
    Store.set('upscaledPokemon', upscaledPokemon)
	Store.set('showSearchMarker', showSearchMarker)
	Store.set('isSearchMarkerMovable', isSearchMarkerMovable)
    Store.set('showLocationMarker', showLocationMarker)
    Store.set('isLocationMarkerMovable', isLocationMarkerMovable)
    Store.set('hidepresets', hidepresets)

    if (typeof window.orientation !== 'undefined' || isMobileDevice()) {
        Store.set('maxClusterZoomLevel', maxClusterZoomLevelMobile)
        Store.set('clusterZoomOnClick', clusterZoomOnClickMobile)
        Store.set('clusterGridSize', clusterGridSizeMobile)
		Store.set('processPokemonChunkSize', processPokemonChunkSizeMobile)
        Store.set('processPokemonIntervalMs', processPokemonIntervalMsMobile)
    }

    if (disableClusters) {
        Store.set('maxClusterZoomLevel', -1)

        if (isMarkerClusterLoaded) {
            window.markerCluster.setMaxZoom(-1)
        }
    }

    // Google Analytics.
    if (analyticsKey.length > 0) {
        window.ga = window.ga || function () {
            (ga.q = ga.q || []).push(arguments)
        }
        ga.l = Date.now
        ga('create', analyticsKey, 'auto')
        ga('send', 'pageview')
    }

    // Show MOTD.
    if (motdEnabled && motdShowOnPages.indexOf(currentPage) !== -1) {
        let motdIsUpdated = true

        if (hasStorage) {
            const lastMOTD = window.localStorage.getItem('lastMOTD') || ''

            if (lastMOTD === motd) {
                motdIsUpdated = false
            }
        }

        if (motdIsUpdated || !motdShowOnlyOnce) {
            window.localStorage.setItem('lastMOTD', motd)

            swal({
                title: motdTitle,
                text: motd
            })
        }
    }
})

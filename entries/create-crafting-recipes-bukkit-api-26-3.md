---
title: "Create's crafting, smelting and stonecutting recipes through the Bukkit API on Paper 26.3"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "VanillaRecipesTest (6 tests) and SurvivalObtainabilityTest#createsCraftingRecipesAreRegistered in plugins/createpaper; Paper 26.3-253 2026-11-19: log '88 Create crafting recipes registered in 202 ms' (108 and 127 ms on later restarts); a bot crafted andesite alloy at a crafting table (item_model createpaper:andesite_alloy); 3 zinc nuggets + leather gave no book while 3 vanilla paper + leather did; raw zinc in a blast furnace gave a zinc ingot"
sources:
  - "research/Recipes on Paper 26.3.md (addRecipes vs addRecipe, PredicateChoice, ingredient matching)"
  - "paper-api-26.3.build.253-stable.jar: ShapedRecipe, ShapelessRecipe, CookingRecipe, StonecuttingRecipe, RecipeChoice, PrepareItemCraftEvent, CrafterCraftEvent, PrepareResultEvent, PlayerPurchaseEvent (javap)"
  - "Create 6.0.11 (MIT): src/generated/resources/data/create/recipe"
date: 2026-11-19
---

# Create's crafting, smelting and stonecutting recipes through the Bukkit API on Paper 26.3

Implemented in `tools/recipe-convert/convert_recipes.py` (writes `recipes/vanilla.json`) and `createpaper.recipe.VanillaRecipes` / `RecipeInstaller`.

## How

- Convert at build time: c: and create: tags are expanded to item ids, `#minecraft:` tags are left for the server. 999 of Create's vanilla-type recipes survive (shaped 375, stonecutting 327, shapeless 273, smelting 16, blasting 6, smoking 1, campfire 1). Smithing transforms (6, netherite gear) aren't converted.
- At enable, keep only recipes whose result exists and whose every ingredient has at least one member here (a vanilla item, or a Create block or item in blocks.json). The rest wait, so new items bring their recipes in on their own.
- Register them all in **one** `Server#addRecipes` call (88 recipes: 108 to 202 ms at startup). Remove them with `removeRecipes` on disable.
- Keys: `new NamespacedKey(plugin, "crafting/kinetics/shaft")`. Slashes are allowed.
- Ingredients: `MaterialChoice` when every member is a vanilla item other than paper. Otherwise use `RecipeChoice.predicateChoice(stack -> ids.contains(recipeId(stack)), example)`, which matches on our PDC id, because every Create item is paper underneath.

## Create items are paper: guard vanilla's paper uses

Without a guard, three zinc nuggets and leather make a book. Clear or cancel when a Create item is involved and the recipe isn't ours:

- `PrepareItemCraftEvent`: `getInventory().setResult(null)`. Proven in game, with vanilla paper as the control.
- `CrafterCraftEvent`: cancel. `PrepareResultEvent` on a `CartographyInventory`: `setResult(null)`. `PlayerPurchaseEvent`: cancel when merchant slot 0 or 1 holds a Create item. These three aren't exercised in game yet.

## Not proven

- Recipe-book display, highlighting and click-to-fill for predicate ingredients on a real client.
- Whether a vanilla stonecutter lists our stonecutting recipes for any paper stack. The server still checks the predicate.

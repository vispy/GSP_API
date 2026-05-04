## 🔹 Persona 1 — *The Scientist Visualizing Their Data*

**Name:** Dr. Alice Researcher

**Role:** Scientist / Research engineer / PhD student

**Background:**

* Domain science (biology, physics, climate, etc.)
* Comfortable with Python, Jupyter, NumPy, but not a graphics expert
* Time-constrained, focused on results & publications

**Goals:**

* Quickly visualize datasets for exploration & papers
* Produce clear plots and interactive figures
* Avoid dealing with rendering pipeline complexity

**Tasks:**

* Load data → call a plotting API → tweak style → export image
* Interactively inspect data (zoom, pick points, animations)
* Share notebook or figure with colleagues

**Motivations:**

* Fast iteration, minimal friction
* Publication-quality visuals
* Ability to scale to large datasets if needed

**Pain Points:**

* Doesn't want to touch shaders or GPU internals
* Large data often makes matplotlib slow
* Hard to install heavy frameworks or GPU-specific libs

**Interaction with GSP:**

* Through higher-level library built on top (not directly)
* Wants simple API like `plot.scatter(data)`

**Must haves:** Easy integration, good defaults, examples
**Nice to haves:** Headless rendering for servers, animations
**Success looks like:** "I tried it, it just worked, and the plot was beautiful."

// pygame_bridge.js

// Step 1: Load Pyodide and Pygame
async function loadPyodideAndPygame() {
    // Load Pyodide
    let pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.21.3/full/",
    });

    // Load the Pygame package
    await pyodide.loadPackage("pygame");

    return pyodide;
}

// Step 2: Set Up the Canvas
function setupCanvas() {
    const canvas = document.createElement("canvas");
    canvas.id = "pygame-canvas";
    canvas.width = 800; // Match your game's WIDTH
    canvas.height = 600; // Match your game's HEIGHT
    document.body.appendChild(canvas);
    return canvas;
}

// Step 3: Forward Browser Events to Pygame
function forwardEvents(pyodide) {
    const canvas = document.getElementById("pygame-canvas");

    // Forward mouse clicks
    canvas.addEventListener("mousedown", (event) => {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        pyodide.runPython(`
            import pygame
            pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (${x}, ${y})}))
        `);
    });

    // Forward keyboard input
    document.addEventListener("keydown", (event) => {
        pyodide.runPython(`
            import pygame
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': ${event.keyCode}}))
        `);
    });
}

// Step 4: Run Pygame Code
async function runPygameCode(pyodide) {
    // Load your Pygame Python code
    const pygameCode = `
        # Your Pygame code here
        import asyncio
        from game import Game

        async def main():
            game = Game()
            await game.run()

        asyncio.run(main())
    `;

    // Execute the Pygame code
    await pyodide.runPythonAsync(pygameCode);
}

// Main function to initialize everything
async function main() {
    const pyodide = await loadPyodideAndPygame();
    setupCanvas();
    forwardEvents(pyodide);
    await runPygameCode(pyodide);
}

// Start the application
main();
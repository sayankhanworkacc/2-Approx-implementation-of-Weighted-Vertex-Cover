# setup.ps1 — install dependencies for weighted_vertex_cover.py

function Try-Install {
    param (
        [Parameter(Mandatory = $true)]
        [array]$CommandsAndDescriptions
    )

    for ($i = 0; $i -lt $CommandsAndDescriptions.Length; $i += 2) {
        $cmd = $CommandsAndDescriptions[$i]
        $desc = $CommandsAndDescriptions[$i + 1]

        Write-Host "Trying to install $desc..."
        try {
            Invoke-Expression $cmd
            Write-Host "$desc installed successfully."
            return
        }
        catch {
            Write-Warning "Failed: $desc. Trying next option..."
        }
    }

    Write-Error "All installation attempts failed."
    exit 1
}

# Call the function with commands + descriptions
Try-Install -CommandsAndDescriptions @(
    "pip install pulp", "PuLP (LP modelling + CBC solver)",
    "python -m pip install pulp", "PuLP via python -m pip",
    "python -m pip install --user pulp", "PuLP with --user flag"
)

Write-Host "Installation complete."
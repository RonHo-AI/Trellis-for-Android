# Analyze Design — Extract Design Tokens

Trigger the UI Designer agent to extract design tokens from screenshots or design descriptions.

Execute these steps:

1. **Check for design input**:
   - Are there screenshots in the task directory or provided by the user?
   - Is there a color palette or dimension spec provided?
   - Is there a reference to an existing design (Figma, image URL, etc.)?

2. **Ensure design-tokens.md template exists**:
   ```bash
   cat specs/design/design-tokens.md 2>/dev/null || echo "No existing tokens"
   ```

3. **Call the UI Designer agent**:
   ```
   Task(
     subagent_type: "ui-designer",
     prompt: "Extract design tokens from the following design input:

   [Paste screenshot path, color values, or design description here]

   Map all extracted values to Android resource types and update specs/design/design-tokens.md."
   )
   ```

   The hook will auto-inject:
   - Design analysis spec files
   - Current design-tokens.md (to preserve existing tokens)

4. **Review the output**:
   ```bash
   cat specs/design/design-tokens.md
   ```

5. **Verify token completeness**:
   - [ ] All UI components have color tokens?
   - [ ] All dimension values are in `dp` or `sp`?
   - [ ] All token names follow `snake_case` convention?
   - [ ] All tokens have a mapped Android resource name?

6. **Proceed to implementation**:
   Once design-tokens.md is complete, run `/trellis:before-dev` to set up for implementation.

## When to Use

| Situation | Action |
|-----------|--------|
| Have a screenshot to implement | Run this command first |
| Have hex color values from designer | Run this command to map to Android resources |
| Don't have any design input | Ask user for design spec before proceeding |
| Design tokens already exist | Skip — go directly to `/trellis:before-dev` |

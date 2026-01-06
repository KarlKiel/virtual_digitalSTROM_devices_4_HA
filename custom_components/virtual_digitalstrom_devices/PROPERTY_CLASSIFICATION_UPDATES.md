# Property Classification Updates

## Summary of Requested Changes

Based on user feedback (comment #3712461568), the following updates are needed to `COMPLETE_PROPERTY_CLASSIFICATION.md`:

### 1. ~~Add `name` Property to General Device Properties (Section 2)~~ - CANCELLED
- **Issue**: User noticed `name` is missing from root/general device properties
- **Resolution**: Checked vDC API spec - there is NO `name` property in General Device Properties
- **Verification**: VDC_PROPERTY_TREE_REFERENCE.md shows General Device Properties only has:
  - primaryGroup, zoneID, progMode, modelFeatures, currentConfigId, configurations
- **Conclusion**: The `name` property in section 14 (Additional Properties) is correct - it's HA-specific, not part of vDC spec
- **Action**: NO CHANGE NEEDED - current classification is correct

### 2. Reclassify `clickType` as META (Section 3.3)
- **Issue**: clickType should be META as it's derived from physical device behavior
- **Current**: STATE
- **Action**: Change category from STATE to META
  - Keep Persisted: ✅ (need to persist the timestamp)
  - Update Derived/Calc: ✅ (derived by behavior method)
  - Update Notes: "Last click type (0-14,255), **derived by physical device behavior**"

### 3. Make Control Values STATE (Persisted) - Section 13
- **Issue**: Control values must be persisted (e.g., heating radiator target temperature)
- **Current**: ACTION category, Write-only, not persisted
- **Action**: Change from ACTION to STATE with persistence
  - Example use case: Heating radiator receives control setting from DSS, if connection breaks, radiator needs last known value
  - heatingLevel, coolingLevel, ventilationLevel, etc. should all be STATE with Persisted: ✅

### 4. Add Req/Opt Column Throughout
- **Issue**: Missing Required/Optional designation per vDC spec
- **Action**: Add "Req/Opt" column to all tables with [R] or [O] markers
  - Update all table headers: Add "Req/Opt" column between "Derived/Calc" and "Notes"
  - Add [R]/[O] markers based on VDC_PROPERTY_TREE_REFERENCE.md

## Implementation Plan

1. ✅ Create this summary document
2. Update Legend to include [R]/[O] definitions
3. Update Section 1 (Root Device Properties) - add Req/Opt column
4. Update Section 2 (General Device Properties) - add name property + Req/Opt column
5. Update Section 3.3 (Button Input States) - change clickType to META + add Req/Opt column
6. Update Sections 4-12 - add Req/Opt column to all tables
7. Update Section 13 (Control Values) - change from ACTION to STATE with persistence
8. Update Section 14 (Additional Properties) - add Req/Opt column
9. Update Summary Statistics to reflect new counts

## Notes

- The Req/Opt markers come from VDC_PROPERTY_TREE_REFERENCE.md
- [R] = Required property per vDC spec
- [O] = Optional property per vDC spec
- Most properties are [R] (required), with specific ones marked [O] (optional) per spec

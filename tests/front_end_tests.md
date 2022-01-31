### Set-up
1. Install Haystack
2. Open GNAT Studio
3. Click "Create new project"
4. Create a "Simple Ada project"
5. Choose a location in which to deploy the project, the rest of the settings don't matter
6. Navigate to the folder where you created the project.
7. Copy the test ada programs from Haystack/tests/test_programs to the src folder of the project you just created.
8. If GNAT Studio is still opened, click File/Project/Reload Project.
9. Now the source files you just added should be visible under src in GNAT Studio.
10. When you click "Find/Find AST", you should see the following window:
![Haystack-Plugin](https://user-images.githubusercontent.com/16014794/151826460-6c6195c9-08a8-4454-974c-7a926953efe6.png)
Only the "Find" and "Find All" buttons on the bottom right should be clickable, the others will enable after finding some matches

### Find functionality
1. Open dosort.adb.
2. Click Find/Find AST to open Haystack.
3. Enter expr_rule in the “Search query parse rule:” box.
4. Enter “Put ($S_expr)” in the Find box.
5. Click “Find”.
6. The Put statement on line 31 should be selected.

### Find All functionality
1. Open dosort.adb.
2. Click Find/Find AST to open Haystack.
3. Enter expr_rule in the “Search query parse rule:” box.
4. Enter “Put ($S_expr)” in the Find box.
5. Click “Find All”.
6. The cursor should be placed on line 31 and the Locations view should be opened. 10 matches should be listed in the Locations view.

### Next/Previous functionality
1. Open dosort.adb.
2. Click Find/Find AST to open Haystack.
3. Enter expr_rule in the “Search query parse rule:” box.
4. Enter “Put ($S_expr)” in the Find box.
5. Click “Find All”.
6. The cursor should be placed on line 31 and the Locations view should be opened. 10 matches should be listed in the Locations view.
7. Clicking “Next” should select the Put statement on line 33 and select the second match in the Locations view.
8. Click “Next” 9 more times and every Put statement should be selected once, wrapping back around to the first match on line 31.
9. Clicking “Previous” once should select the last Put statement on line 195, clicking “Previous” 9 more times should move through the selections back to the first selection on line 31.

### Replace Next functionality
1. Open dosort.adb.
2. Click Find/Find AST to open Haystack.
3. Enter expr_rule in the “Search query parse rule:” box.
4. Enter “Put ($S_expr)” in the Find box.
5. Click “Find”.
6. The Put statement on line 31 should be selected.
7. Enter “Put_Line ($S_expr)” in the Replace box.
8. Click “Replace Next”
9. Line 31 should now read “Put_Line (“[“);” and the next match on line 33 should be selected.
10. Undo the change by pressing ctrl+z in the editor and saving with ctrl+s.

### Replace All functionality
1. Open dosort.adb.
2. Click Find/Find AST to open Haystack.
3. Enter expr_rule in the “Search query parse rule:” box.
4. Enter “Put ($S_expr)” in the Find box.
5. Click “Find”.
6. The Put statement on line 31 should be selected.
7. Enter “Put_Line ($S_expr)” in the Replace box.
8. Click “Replace All”
9. Line 31 should now read “Put_Line (“[“);”. Similarly, all other Put statements should now also be replaced by Put_Line statements.
10. Undo the change by pressing ctrl+z in the editor and saving with ctrl+s.

### Search context functionality
1. Click Find/Find AST to open Haystack.
2. Enter expr_rule in the “Search query parse rule:” box.
3. Enter “Put ($S_expr)” in the Find box.
4. Select “Files from current project” in the “Where” box.
5. Click “Find All”.
6. All files in the project should now be opened, the first match on line 31 of dosort.adb should be selected. In the Locations view it should display that it found 23 matches in 4 files, these files being dosort.adb with 10 matches, g_stack_user.adb with 4 matches, hello.adb with 3 matches and obj1.adb with 6 matches.
7. Clicking “Next” or “Previous” should cycle you through all found matches, even those in files other than the one you’re currently looking at.

### Case insensitive functionality
1. Open dosort.adb.
2. Click Find/Find AST to open Haystack.
3. Enter expr_rule in the “Search query parse rule:” box.
4. Enter “put ($S_expr)” in the Find box.
5. Click “Find All”.
6. The cursor should not be moved and no matches should be found, the Locations view should remain empty.
7. Tick “Case insensitive”
8. Click “Find All”.
9. The cursor should be placed on line 31 and the Locations view should be opened. 10 matches should be listed in the Locations view.

### Try-rules functionality
1. Open dosort.adb.
2. Click Find/Find AST to open Haystack.
3. Enter “Put ($S_expr)” in the Find box.
4. Click “Find All”.
5. The “Try other rules?” window should open.
6. Select “Yes” and click “Ok”.
7. After a short while, the cursor should be placed on line 31 and the Locations view should be opened. 10 matches should be listed in the Locations view.

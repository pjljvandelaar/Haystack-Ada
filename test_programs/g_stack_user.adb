--
-- A client of the G_Stack package.
--

with Ada.Text_IO; use Ada.Text_IO;
with Ada.Integer_Text_IO; use Ada.Integer_Text_IO;
with G_Stack;

procedure G_Stack_User is
   -- Now create two stack packages from the generic one.
   package Small_Int_Stack is new G_Stack(10, Integer);
   use Small_Int_Stack;
   subtype Stackable_String is String(1..60);
   package Big_String_Stack is new G_Stack(300, Stackable_String);
   use Big_String_Stack;

   -- We cannot not create a stack of indefinite Strings with this
   -- package, but we can do this:
   type String_Ptr is access String;
   package String_Ptr_Stack is new G_Stack(55, String_Ptr);
   use String_Ptr_Stack;

   -- Here are variables of those types.  Since we have multiple
   -- instantiations, and each contains Gen_Stack, we have to qualify:
   IStack: Small_Int_Stack.Gen_Stack;
   SStack: Big_String_Stack.Gen_Stack;
   SPStack: String_Ptr_Stack.Gen_Stack;

   -- Here some exciting input variables.
   Exciting: Integer;
   Stupendous: Stackable_String;
   Input_Size: Integer;                 -- Size of string read.

   -- A variable for getting string pointers from Pop.
   Popped: String_Ptr;
begin
   -- Read in some integers, and push 'em
   begin
      Put_Line("How about some nice integers?");
      loop
         Put("> ");
         Get(Exciting);
         Push(IStack, Exciting);
         -- Note: Push is not ambiguous because of the argument types.  If
         -- we had created and used another integer stack with a different
         -- size, then we would have to qualify here.
      end loop;
   exception
      when End_Error =>
         -- Mostly just leave the loop, but this looks cleaner sometimes.
         New_Line;
      when Small_Int_Stack.Stack_Overflow =>
         -- Note: The qualification on Stack_Overflow is required by the
         -- multiple instantiations.  There are no arguments to an exception
         -- to tell them apart.
         Put_Line("Stack Overflow.  Input Terminated.");
      when Data_Error =>
         -- Figure user just started using strings.  Next loop will read
         -- the data
         Put_Line("Okay, that'll be your first string.");
   end;

   -- Now read in some strings.  After reading, strings are padded with
   -- blanks.
   begin
      Put_Line("How about some nice strings?");
      loop
         -- Prompt and read.
         Put("> ");
         Get_Line(Stupendous, Input_Size);

         -- Exit when done.
         exit when Stupendous(1..Input_Size) = "quit";

         -- Not done, so fill the rest of the array and push it on the stack.
         Stupendous(Input_Size+1..Stupendous'Last) :=
           (Input_Size+1..Stupendous'Last => ' ');
         Push(SStack, Stupendous);
      end loop;
   exception
      when End_Error =>
         -- Mostly just leave the loop, but this looks cleaner sometimes.
         New_Line;
      when Big_String_Stack.Stack_Overflow =>
         Put_Line("Stack Overflow.  Input Terminated.");
   end;

   -- Now read in some more strings.  Dynamic copies will be made and pointers
   -- pushed for this bunch.
   begin
      Put_Line("How about more some nice strings?");
      loop
         -- Prompt and read.
         Put("> ");
         Get_Line(Stupendous, Input_Size);

         -- Exit when done.
         exit when Stupendous(1..Input_Size) = "quit";

         -- Not done, so fill the rest of the array and push it on the stack.
         Push(SPStack, new String'(Stupendous(1..Input_Size)));
      end loop;
   exception
      when End_Error =>
         -- Mostly just leave the loop, but this looks cleaner sometimes.
         New_Line;
      when String_Ptr_Stack.Stack_Overflow =>
         Put_Line("Stack Overflow.  Input Terminated.");
      when others =>
         -- Just because I haven't shown you when others.  This catches
         -- any exception not caught by the others.
         Put_Line("Something unexpected went wrong");
   end;

   -- Pop 'n and print the integers.
   loop
      Pop(IStack, Exciting);
      Put(Exciting, 1);
      exit when Empty(IStack);
      Put(" ");
   end loop;
   New_Line;

   -- First bunch of strings.
   New_Line;
   loop
      Pop(SStack, Stupendous);
      Put_Line("[" & Stupendous & "]");
      exit when Empty(SStack);
   end loop;

   -- Second bunch of strings.
   New_Line;
   loop
      Pop(SPStack, Popped);
      Put_Line("[" & Popped.all & "]");
      exit when Empty(SPSTack);
   end loop;
end G_Stack_User;

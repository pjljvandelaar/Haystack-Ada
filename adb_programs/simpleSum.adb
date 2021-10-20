with Ada.Text_IO, Ada.Integer_Text_IO, Ada.Float_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO, Ada.Float_Text_IO;

procedure First is

  Number_Of_Values: Integer;           -- variable declaration
  Sum: Integer := 0;                   -- variable declaration w/ initializer

begin
  Put ("Enter an integer: ");          -- put a string
  Get (Number_Of_Values);              -- get an integer
  for I in 1..Number_Of_Values loop    -- note the implicit declaration of I
    Put (I);                           -- put an integer
    Put (',');                         -- put a character
    Sum := Sum + I;
  end loop;                            -- variable I does not exist after loop
  New_Line (2);                        -- call New_Line with an argument
  Put ("The sum is ");                 -- put a string
  Put (Sum);
  New_Line;                            -- call New_Line with default argument
  Put ("The average is ");
  Put (Float(Sum) / Float(Number_Of_Values));
  New_Line;
end First;
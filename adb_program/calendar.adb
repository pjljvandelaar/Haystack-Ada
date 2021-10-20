
------------------------------------------------------------------
--  This procedure displays messages about the current date, such 
--  as which half-year, quarter-year, or season we are in. 
------------------------------------------------------------------
with Ada.Text_IO, Ada.Calendar;
use  Ada.Text_IO;
procedure Main is
                                              -- declarative part
  The_Time  : Ada.Calendar.Time;
  The_Month : Ada.Calendar.Month_Number;
  The_Day   : Ada.Calendar.Day_Number;

  type Month_Abr is (Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec);
  Month_Abbreviation : Month_Abr;

begin                                         -- executable part

  The_Time  := Ada.Calendar.Clock;
  The_Month := Ada.Calendar.Month(The_Time);
  The_Day   := Ada.Calendar.Day(The_Time);

  Month_Abbreviation := Month_Abr'Val(The_Month);

  if The_Month < 7 then                       -- simple if statement
    Put_Line("We are in the first half year.");
  end if;

  if The_Month < 7 then                       -- if-else statement
    Put_Line("We are in the first half.");
  else
    Put_Line("We are in the second half.");
  end if;

  if The_Month < 4 then                       -- if-elsif-else statement
    Put_Line("We are in the first quarter.");
  elsif The_Month < 7 then
    Put_Line("We are in the second quarter.");
  elsif The_Month < 10 then
    Put_Line("We are in the third quarter.");
  else
    Put_Line("We are in the fourth quarter.");
  end if;

  if The_Month < 3 then                       -- nested if statements
    Put_Line("The season is Winter.");
  elsif The_Month = 3 then
    if The_Day < 21 then 
      Put_Line("The season is Winter.");
    else
      Put_Line("The season is Spring.");
    end if;
  elsif The_Month < 6 then
    Put_Line("The season is Spring.");
  elsif The_Month = 6 then
    if The_Day < 21 then
      Put_Line("The season is Spring.");
    else
      Put_Line("The season is Summer.");
    end if;
  elsif The_Month < 9 then
    Put_Line("The season is Summer."); 
  elsif The_Month = 9 then
    if The_Day < 21 then
      Put_Line("The season is Summer.");
    else
      Put_Line("The season is Fall.");
    end if;
  elsif The_Month < 12 then
    Put_Line("The season is Fall.");
  elsif The_Month = 12 then
    if The_Day < 21 then
      Put_Line("The season is Fall.");
    else
      Put_Line("The season is Winter.");
    end if;
  end if;

  if (The_Month = 12 and The_Day >= 21) or  -- if with logical operators
     (The_Month = 1) or (The_Month = 2) or
     (The_Month = 3  and The_Day < 21) then
    Put_Line("The season is Winter.");
     
  elsif (The_Month = 3 and The_Day >= 21) or
        (The_Month = 4) or (The_Month = 5) or
        (The_Month = 6 and The_Day < 21) then
    Put_Line("The season is Spring.");

  elsif (The_Month = 6 and The_Day >= 21) or
        (The_Month = 7) or (The_Month = 8) or
        (The_Month = 9 and The_Day < 21) then
    Put_Line("The season is Summer.");

  else 
    Put_Line("The season is Fall.");
  end if;

end Main;
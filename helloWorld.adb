-- comment
procedure Main is
   The_Time : Ada.Calendar.Time;
   The_Month : Ada.Calendar.Month_Number;
begin
   Put_Line ("Hello, World!");
   if The_Month < 7 then
      Put_Line("We are in the first half year.");
   end if;
end Main;
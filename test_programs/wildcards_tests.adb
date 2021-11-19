-- comment
procedure Main is
   The_Time : Ada.Calendar.Time;
   The_Month : Integer;
begin
   Put(Arr(II).X);
   Put(Arr(I).X);
   if The_Month < 7 then
      Put(Arr(I).X);
      Put_Line ("Hello, World!");
      Put_Line("We are in the first half year.");
   end if;
   if The_Month > The_Time then
      The_Month := The_Time;
   end if;
end Main;
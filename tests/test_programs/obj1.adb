with Gnat.Io; use Gnat.Io;
procedure Obj1 is
   -- Type of counter objects.  It is an object only in that it is "tagged,"
   -- which means that it has extra space assigned by the system to retain
   -- its dynamic type (just like Java objects and C++ objects with virtual
   -- functions).
   type Counter is tagged record
      Count: Integer := 0;
   end record;

   -- Operations on counter objects.  The attribute 'Class essentially means,
   -- "and derived classes, too".  If it were omitted, the call Inc(A)
   -- below (for A which is the derived type accumulator) would be illegal.

   -- Print the Counter.
   procedure Put(C: Counter'Class) is
   begin
      Put(C.Count);
   end Put;

   -- Increment the counter by 1.
   procedure Inc(C: in out Counter'Class) is
   begin
      C.Count := C.Count + 1;
   end Inc;

   -- Limited counters will not increment past a certain maximum.
   type Limited_Counter is new Counter with record
      Limit: Integer := 1;
   end record;

   -- Operations for Limited_Counter

   -- Set the limit.
   procedure Limit_To(LC: in out Limited_Counter'Class; L: Integer) is
   begin
      LC.Limit := L;
      if LC.Count > L then LC.Count := L; end if;
   end Limit_To;

   -- Increment.
   procedure Inc(LC: in out Limited_Counter'Class) is
   begin
      Inc(Counter(LC));
      if LC.Count > LC.Limit then LC.Count := LC.Limit; end if;
   end Inc;

   -- Accumulator objects can be incremented by an arbitrary amount (not
   -- just one!  Wow!)  This requires no additional data fields.
   type Accumulator is new Counter with null record;

   -- Operation specific to Accumulator: Increment by arbitrary amount.
   procedure Inc(C: in out Accumulator'Class; Amt: Integer) is
   begin
      C.Count := C.Count + Amt;
   end Inc;

   -- Some example variables.
   C: Counter;
   L: Limited_Counter;
   A: Accumulator;

begin
   Inc(C);
   Limit_To(L, 3); Inc(LC => L); Inc(LC => L);
                   Inc(LC => L); Inc(LC => L); Inc(LC => L);
   Inc(A);
   Inc(A, 4);
   Put(A); Put(" "); Put(L); Put(" "); Put(C); New_Line;
end Obj1;

-- Note: I needed LC => L to get it to resolve Inc.  This is absurd, but I
-- have not figured out if there's something different I need to declare, or
-- the language is just absurd on this point.

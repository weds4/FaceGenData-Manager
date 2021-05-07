{
  New script template, only shows processed records
  Assigning any nonzero value to Result will terminate script
}
unit userscript;
uses 'lib\mteFunctions';
var 
  patch: IwbFile;

// Called before processing
// You can remove it if script doesn't require initialization code
function Initialize: integer;
begin
  patch := FileByName('NPC_Manager.esp');
  if not Assigned(patch) then patch := AddNewFileName('NPC_Manager.esp', true);
  Result := 0;
end;

// called for every record selected in xEdit
function Process(e: IInterface): integer;
begin
  Result := 0;
  AddMessage('Processing '+FullPath(e));
  AddRequiredElementMasters(e, patch, False);
  wbCopyElementToFile(e, patch, False, True);
  if GetElementNativeValues(e, 'ACBS\Template Flags\Use Traits') <> -1 then ShellExecuteWait(0, nil, 'NPC_Manager.exe', FullPath(e), nil, SW_SHOWNORMAL);

end;

// Called after processing
// You can remove it if script doesn't require finalization code
function Finalize: integer;
begin
  CleanMasters(patch);
  Result := 0;
end;

end.

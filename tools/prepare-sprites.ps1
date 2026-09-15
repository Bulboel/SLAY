param(
  [string]$NickySource = 'C:\Users\Jojo\AppData\Local\Temp\codex-clipboard-ccfb3788-3761-463d-8d20-169f591ac188.png',
  [string]$AssetDir = (Join-Path $PSScriptRoot '..\dist\assets')
)

Add-Type -AssemblyName System.Drawing

function New-TransparentCrop {
  param([System.Drawing.Bitmap]$Source,[System.Drawing.Rectangle]$Rect,[int]$Width,[int]$Height,[string]$Output)
  $target = [System.Drawing.Bitmap]::new($Width,$Height,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g = [System.Drawing.Graphics]::FromImage($target)
  $g.Clear([System.Drawing.Color]::Transparent)
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
  $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
  $g.DrawImage($Source,[System.Drawing.Rectangle]::new(0,0,$Width,$Height),$Rect,[System.Drawing.GraphicsUnit]::Pixel)
  $g.Dispose()
  for($y=0;$y -lt $Height;$y++) { for($x=0;$x -lt $Width;$x++) {
    $c=$target.GetPixel($x,$y); $hi=[Math]::Max($c.R,[Math]::Max($c.G,$c.B)); $lo=[Math]::Min($c.R,[Math]::Min($c.G,$c.B))
    if(($lo -gt 142 -and ($hi-$lo) -lt 42) -or ($c.R -gt 242 -and $c.G -gt 242 -and $c.B -gt 242)) { $target.SetPixel($x,$y,[System.Drawing.Color]::Transparent) }
  }}
  $target.Save($Output,[System.Drawing.Imaging.ImageFormat]::Png); $target.Dispose()
}

function Split-BattleSheet {
  param([string]$SourcePath,[string]$Prefix)
  $source=[System.Drawing.Bitmap]::FromFile($SourcePath); $w=[int]($source.Width/2); $h=[int]($source.Height/2)
  $states=@('normal','attack','hit','down')
  for($i=0;$i -lt 4;$i++) { New-TransparentCrop $source ([System.Drawing.Rectangle]::new(($i%2)*$w,[int][Math]::Floor($i/2)*$h,$w,$h)) 384 384 (Join-Path $AssetDir "$Prefix-$($states[$i])-v3.png") }
  $source.Dispose()
}

function Normalize-Strip {
  param([string]$SourcePath,[string]$Output)
  $source=[System.Drawing.Bitmap]::FromFile($SourcePath); $cellW=[int]($source.Width/4); $cellH=$source.Height
  $target=[System.Drawing.Bitmap]::new(384,96,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $tg=[System.Drawing.Graphics]::FromImage($target); $tg.Clear([System.Drawing.Color]::Transparent); $tg.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
  for($i=0;$i -lt 4;$i++) {
    $minX=$cellW; $minY=$cellH; $maxX=0; $maxY=0
    for($y=0;$y -lt $cellH;$y+=2) { for($x=0;$x -lt $cellW;$x+=2) { if($source.GetPixel($i*$cellW+$x,$y).A -gt 20) { $minX=[Math]::Min($minX,$x);$minY=[Math]::Min($minY,$y);$maxX=[Math]::Max($maxX,$x);$maxY=[Math]::Max($maxY,$y) } } }
    $cw=[Math]::Max(1,$maxX-$minX+2); $ch=[Math]::Max(1,$maxY-$minY+2); $scale=[Math]::Min(88/$cw,88/$ch); $dw=[int]($cw*$scale);$dh=[int]($ch*$scale);$dx=$i*96+[int]((96-$dw)/2);$dy=96-$dh
    $tg.DrawImage($source,[System.Drawing.Rectangle]::new($dx,$dy,$dw,$dh),[System.Drawing.Rectangle]::new($i*$cellW+$minX,$minY,$cw,$ch),[System.Drawing.GraphicsUnit]::Pixel)
  }
  $tg.Dispose();$target.Save($Output,[System.Drawing.Imaging.ImageFormat]::Png);$target.Dispose();$source.Dispose()
}

function Test-SpriteAsset {
  param([string]$Path,[int]$ExpectedWidth,[int]$ExpectedHeight)
  if(!(Test-Path -LiteralPath $Path)){ throw "Sprite absent : $Path" }
  $bitmap=[System.Drawing.Bitmap]::FromFile($Path)
  if($bitmap.Width -ne $ExpectedWidth -or $bitmap.Height -ne $ExpectedHeight){$actual="$($bitmap.Width)x$($bitmap.Height)";$bitmap.Dispose();throw "Dimensions invalides pour $Path : $actual, attendu ${ExpectedWidth}x${ExpectedHeight}"}
  $transparent=0;$opaque=0
  for($y=0;$y -lt $bitmap.Height;$y+=4){for($x=0;$x -lt $bitmap.Width;$x+=4){if($bitmap.GetPixel($x,$y).A -lt 20){$transparent++}else{$opaque++}}}
  $bitmap.Dispose()
  if($transparent -lt 20){throw "Transparence absente ou damier probablement incrusté : $Path"}
  if($opaque -lt 20){throw "Sprite vide après détourage : $Path"}
  Write-Output "OK  $([IO.Path]::GetFileName($Path))  ${ExpectedWidth}x${ExpectedHeight}  alpha=$transparent  sujet=$opaque"
}

$nicky=[System.Drawing.Bitmap]::FromFile($NickySource)
New-TransparentCrop $nicky ([System.Drawing.Rectangle]::new(120,0,500,540)) 500 540 (Join-Path $AssetDir 'portrait-nicky-v1.png')
$sheet=[System.Drawing.Bitmap]::new(256,80,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$sheetGraphics=[System.Drawing.Graphics]::FromImage($sheet); $sheetGraphics.Clear([System.Drawing.Color]::Transparent); $sheetGraphics.Dispose()
$frames=@(
  [System.Drawing.Rectangle]::new(1265,18,150,150),
  [System.Drawing.Rectangle]::new(775,60,120,135),
  [System.Drawing.Rectangle]::new(750,330,145,150),
  [System.Drawing.Rectangle]::new(760,185,145,155)
)
for($i=0;$i -lt 4;$i++) {
  $temp=Join-Path $AssetDir "_nicky-$i.png"; New-TransparentCrop $nicky $frames[$i] 64 80 $temp
  $frame=[System.Drawing.Bitmap]::FromFile($temp); $g=[System.Drawing.Graphics]::FromImage($sheet); $g.DrawImageUnscaled($frame,$i*64,0); $g.Dispose(); $frame.Dispose(); Remove-Item -LiteralPath $temp
}
$sheet.Save((Join-Path $AssetDir 'nicky-map-v1.png'),[System.Drawing.Imaging.ImageFormat]::Png); $sheet.Dispose(); $nicky.Dispose()

Split-BattleSheet (Join-Path $AssetDir 'sexyflex-battle-v2.png') 'sexyflex'
Split-BattleSheet (Join-Path $AssetDir 'dantonlix-battle-v2.png') 'dantonlix'
Normalize-Strip (Join-Path $AssetDir 'sexyflex-map-v1.png') (Join-Path $AssetDir 'sexyflex-map-v2.png')
Normalize-Strip (Join-Path $AssetDir 'veloursa-map-v1.png') (Join-Path $AssetDir 'veloursa-map-v2.png')

@('sexyflex','dantonlix') | ForEach-Object { $name=$_; @('normal','attack','hit','down') | ForEach-Object { Test-SpriteAsset (Join-Path $AssetDir "$name-$_-v3.png") 384 384 } }
Test-SpriteAsset (Join-Path $AssetDir 'sexyflex-map-v2.png') 384 96
Test-SpriteAsset (Join-Path $AssetDir 'veloursa-map-v2.png') 384 96
Test-SpriteAsset (Join-Path $AssetDir 'nicky-map-v1.png') 256 80


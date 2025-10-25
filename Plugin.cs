using System.IO;
using System.Reflection;
using BepInEx;
using BepInEx.Logging;
using BepInEx.Unity.IL2CPP;
using HarmonyLib;
using Pipistrello;

namespace PipistrelloHan
{
    [BepInPlugin("PipistrelloHan.RuntimePatcher", "PipistrelloHan Runtime Patcher", "1.0.0")]
    public class Plugin : BasePlugin
    {
        public static ManualLogSource Logger;

        public override void Load()
        {
            Logger = base.Log;

            Logger.LogInfo("PipistrelloHan Runtime Patcher loaded. Applying Harmony patches...");
            Harmony.CreateAndPatchAll(typeof(Hooks));
        }
    }

    public static class Hooks
    {
        private static bool hasPatched = false;


        [HarmonyPatch(typeof(Global), MethodType.StaticConstructor)]
        [HarmonyPostfix]
        public static void PatchStaticConstructor()
        {
            Plugin.Logger.LogInfo("Static constructor called! Patching fontCharRanges...");
            PatchFontCharRanges();
        }

        // 也 patch Init 方法作为备份
        [HarmonyPatch(typeof(Global), "Init")]
        [HarmonyPrefix]
        public static void PatchInitPrefix()
        {
            Plugin.Logger.LogInfo("Init() prefix called! Patching fontCharRanges...");
            PatchFontCharRanges();
        }

        private static void PatchFontCharRanges()
        {
            // 防止重复执行
            if (hasPatched)
            {
                Plugin.Logger.LogInfo("Already patched, skipping...");
                return;
            }

            if (Global.fontCharRanges == null || Global.fontCharRanges.Length == 0)
            {
                Plugin.Logger.LogWarning("Global.fontCharRanges is null or empty. Will try again later.");
                return;
            }

            hasPatched = true;
            Plugin.Logger.LogInfo("=== Starting font character patch ===");

            char[] originalChars = Global.fontCharRanges;
            Plugin.Logger.LogInfo($"Original fontCharRanges length: {originalChars.Length}");

            // 添加新字符到数组末尾（每个字符重复两次，符合原数组格式）
            Plugin.Logger.LogInfo("=== Replacing old doubled characters with new characters ===");
            var assembly = Assembly.GetExecutingAssembly();
            StreamReader sr = new(assembly.GetManifestResourceStream("PipistrelloHan.resources.unique_chinese_chars.txt"));
            string newChars = sr.ReadToEnd().Trim();
            Plugin.Logger.LogInfo($"New characters count: {newChars.Length}");
            // 另外添加两个字符：后引号”和间隔符号·
            string newSymbolChars = "”·";

            // 查找原数组中连续两个'一'的位置（一一），这才是重复中文字符区的真正起点
            int originalLength = originalChars.Length;
            int startRemoveIndex = -1;
            int tmIndex = -1;
            for (int i = 0; i < originalLength - 1; i++)
            {
                if (originalChars[i] == '™' && originalChars[i + 1] == '™' && tmIndex == -1)
                {
                    tmIndex = i;
                    Plugin.Logger.LogInfo($"Found '™' at index {i}");
                }
                if (originalChars[i] == '一' && originalChars[i + 1] == '一')
                {
                    startRemoveIndex = i;
                    Plugin.Logger.LogInfo($"Found '一一' at index {i}");
                    break;
                }
            }

            if (startRemoveIndex == -1)
            {
                Plugin.Logger.LogWarning("Could not find '一一' in original array, skipping removal.");
                return;
            }

            if (tmIndex == -1)
            {
                Plugin.Logger.LogWarning("Could not find '™' in original array.");
                return;
            }

            Plugin.Logger.LogInfo($"Will remove from index {startRemoveIndex} to end, keeping first {startRemoveIndex} characters.");

            // 创建新的数组：保留的原字符 + 新字符*2 + 新符号字符*2
            char[] newArray = new char[startRemoveIndex + newChars.Length * 2 + newSymbolChars.Length * 2];

            // 复制原有字符（从最开始到'™'的部分）
            System.Array.Copy(originalChars, 0, newArray, 0, tmIndex + 2);

            // 添加新符号字符到数组中，每个字符重复两次
            int symbolIndex = tmIndex + 2;
            for (int i = 0; i < newSymbolChars.Length; i++)
            {
                Plugin.Logger.LogInfo($"  Adding symbol '{newSymbolChars[i]}' = U+{((int)newSymbolChars[i]):X4} at indices [{symbolIndex}] and [{symbolIndex + 1}]");
                newArray[symbolIndex] = newSymbolChars[i];
                newArray[symbolIndex + 1] = newSymbolChars[i];
                symbolIndex += 2;
            }

            // 复制原有字符（从'™'后面到"一一"的部分）
            System.Array.Copy(originalChars, tmIndex + 2, newArray, symbolIndex, startRemoveIndex - (tmIndex + newSymbolChars.Length));

            // 添加新字符到末尾，每个字符重复两次
            int index = startRemoveIndex + newSymbolChars.Length * 2;
            for (int i = 0; i < newChars.Length; i++)
            {
                newArray[index] = newChars[i];
                newArray[index + 1] = newChars[i];
                // 只记录前10个和后10个，避免日志过多
                if (i < 10 || i >= newChars.Length - 10)
                {
                    Plugin.Logger.LogInfo($"  Added [{index}] and [{index + 1}] '{newChars[i]}' = U+{((int)newChars[i]):X4}");
                }
                index += 2;
            }

            Plugin.Logger.LogInfo($"New array length: {newArray.Length} (original: {originalLength}, added: {newChars.Length * 2})");

            // 将修改后的数组写回到 Global.fontCharRanges
            Global.fontCharRanges = newArray;
            Plugin.Logger.LogInfo("Successfully updated Global.fontCharRanges with new characters!");
        }
    }
}
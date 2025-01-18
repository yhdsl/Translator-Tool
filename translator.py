"""
文件翻译器

根据指定的源文件内的规则，
对目标文件进行文本替换

请通过命令行参数进行操作
"""

import argparse
import os
import pathlib


# 命令行处理部分

parser = argparse.ArgumentParser()

parser.add_argument('SOURCE', action='store',
                    help='the source file or folder address')
parser.add_argument('-r', '--root', action='store', dest='TARGET_ROOT',
                    help='the target file or folder root address')

args_dict = vars(parser.parse_args())

SOURCE_ADDRESS: str = args_dict['SOURCE']
TARGET_ROOT_ADDRESS: str | None = args_dict['TARGET_ROOT']


# 规则文件处理部分

class RuleFile:
    def __init__(self, source_path: pathlib.Path):
        """
        :param source_path:
            规则文件地址
        """
        self.delimiter = '='  # 默认分隔符

        self._metadata_dict, self.rule_dict = self.get_metadata_and_rule(source_path)

        if TARGET_ROOT_ADDRESS is not None:
            os.chdir(TARGET_ROOT_ADDRESS)
        try:
            self._target_address = self._metadata_dict['TARGET']
        except IndexError as e:
            raise ValueError("metadata without target address.") from e
        self.target_path = pathlib.Path(self._target_address)
        self.target_path.absolute()
        if not self.target_path.is_file():
            raise FileNotFoundError(f"{str(self.target_path)} is not a file.")

        return

    def get_metadata_and_rule(self, path: pathlib.Path):
        """
        处理规则文件，
        拆分得到元数据和替换规则

        规则文件的语法请参考示例文件

        :param path:
            规则文件地址

        :return:
            元数据和替换规则对应的字典
        """
        with path.open(mode='r', encoding='utf8') as fp:
            text_list = fp.readlines()

        metadata_dict: dict[str, str] = {}
        rule_dict: dict[str, str] = {}
        metadata_fin = False
        for line in text_list:
            # 清空换行符
            if line[-1] == '\n':
                line = line[:-1]

            # 跳过空行
            if line == '':
                continue

            # 处理文件头部的元数据
            if not metadata_fin:
                if line[0] == '@':
                    try:
                        metadata_name, metadata_value = line[1:].split(self.delimiter, maxsplit=1)
                        metadata_dict[metadata_name] = metadata_value
                    except ValueError:
                        pass
                    finally:
                        continue
                else:
                    try:
                        self.delimiter = metadata_dict['DELIMITER']
                    except KeyError:
                        pass
                    metadata_fin = True

            # 跳过注释
            if line[0] == '#':
                continue

            # 处理可以被拆分的规则行
            line_rules = line.rsplit(self.delimiter, maxsplit=1)
            if len(line_rules) == 1:
                continue
            else:
                rule_dict[line_rules[0]] = line_rules[1]

        return metadata_dict, rule_dict

    def target_replace(self):
        """
        根据规则对目标文件进行替换
        """
        print(f"### {str(self.target_path)}")
        with self.target_path.open(mode='r', encoding='utf8') as fp1:
            text = ''.join(fp1.readlines())

        for rule_name in self.rule_dict:
            rule_value = self.rule_dict[rule_name]
            if rule_name in text:
                print(f"{rule_name} --> {rule_value}")
            text = text.replace(rule_name, rule_value, 1)

        with self.target_path.open(mode='w+', encoding='utf8') as fp2:
            fp2.write(text)

        return


# 程序入口部分

def main():
    source_path = pathlib.Path(SOURCE_ADDRESS)
    source_file_list: list[pathlib.Path] = []
    if source_path.is_file():
        source_file_list.append(source_path.absolute())
    elif source_path.is_dir():
        source_file_list.extend([address.absolute()
                                 for address in source_path.glob('**/*')
                                 if address.is_file()])
    else:
        raise TypeError(f"{SOURCE_ADDRESS} is not a file or folder.")

    for rule_path in source_file_list:
        rule = RuleFile(rule_path)
        rule.target_replace()

    return


if __name__ == '__main__':
    main()

import re

def split_and_overlap(sub_lines, max_chunk_size=5500, overlap=500):
    """
    将子行按最大长度进行拆分，并添加重叠区域
    :param sub_lines: 当前标题下的行
    :param max_chunk_size: 每块的最大字符长度
    :param overlap: 块与块之间的重叠字符数
    :return: 拆分后的块列表
    """
    sub_chunks = []
    current_chunk = ""

    for line in sub_lines:
        line_length = len(line) + 1  # 加换行
        if len(current_chunk) + line_length > max_chunk_size:
            sub_chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            current_chunk += '\n' + line if current_chunk else line

    if current_chunk:
        sub_chunks.append(current_chunk.strip())

    # 添加重叠部分
    final_chunks = []
    for i, chunk in enumerate(sub_chunks):
        if i > 0:
            prev = sub_chunks[i - 1]
            overlap_text = prev[-overlap:] if len(prev) > overlap else prev
            chunk = overlap_text + '\n' + chunk
        final_chunks.append(chunk)

    return final_chunks

def split_markdown_into_chunks(markdown_text, max_chunk_size=5500, overlap=500):
    # 根据每行是否以 '#' 开头确定标题行索引
    title_indices = []
    lines = markdown_text.split('\n')
    # 直接将所有行的索引添加到列表中
    title_indices = list(range(len(lines)))
    # #以特殊标志划分，此处为\xa0
    # for i, line in enumerate(lines):
    #     if line.startswith('\xa0'):
    #         title_indices.append(i)
    # title_indices.append(len(lines))  # 添加结束索引

    chunks = []
    chunk_count = 0
    print(len(title_indices))
    if len(title_indices) <= 2:
        start = title_indices[0]
        end = title_indices[1]
        current_block = lines[start:end]
        sub_chunks = split_and_overlap(current_block, max_chunk_size, overlap)
        chunks.extend(sub_chunks)
    else:
        for i in range(len(title_indices) - 1):
            start = title_indices[i]
            end = title_indices[i + 1]
            current_block = '\n'.join(lines[start:end])

            # 处理第一个块
            if not chunks:
                if len(current_block) > max_chunk_size:
                    sub_chunks = split_and_overlap(lines[start:end], max_chunk_size, overlap)
                    chunks.extend(sub_chunks)
                else:
                    chunks.append(current_block)
                print(f"[CHUNK {chunk_count}] length = {len(current_block)}")
                chunk_count += len(sub_chunks) if len(current_block) > max_chunk_size else 1
                continue

            # 对于后续块：从前一块获取末尾 overlap 部分作为前缀
            prev_chunk = chunks[-1]
            tail_overlap = prev_chunk[-overlap:] if len(prev_chunk) > overlap else prev_chunk

            # 尝试直接将当前块合并到前一块（直接合并无额外重复前缀）
            merged_chunk = prev_chunk + '\n' + current_block
            if len(merged_chunk) <= max_chunk_size:
                chunks[-1] = merged_chunk
                print(f"[CHUNK {chunk_count - 1}] merged, new length = {len(merged_chunk)}")
                continue

            # 否则，新块加入时先在前面添加重叠前缀
            new_chunk = tail_overlap + '\n' + current_block
            if len(new_chunk) <= max_chunk_size:
                chunks.append(new_chunk)
                print(f"[CHUNK {chunk_count}] new chunk with overlap, length = {len(new_chunk)}")
                chunk_count += 1
            else:
                # 如果当前块（含重叠前缀）超过限制，则对子块进行拆分处理
                sub_chunks = []
                current_sub_start = start
                for j in range(start + 1, end + 1):
                    candidate = '\n'.join(lines[current_sub_start:j])
                    # 移除重复的标题部分
                    overlap_without_title = tail_overlap
                    for line in lines[:start]:
                        if line in overlap_without_title:
                            overlap_without_title = overlap_without_title.replace(line, '').strip()
                    candidate_with_overlap = overlap_without_title + '\n' + candidate if overlap_without_title else candidate
                    if len(candidate_with_overlap) > max_chunk_size:
                        # 动态调整重叠（以行计），减少重叠行数
                        overlap_lines = overlap
                        while overlap_lines > 0:
                            overlap_without_title = '\n'.join(tail_overlap.split('\n')[-overlap_lines:])
                            for line in lines[:start]:
                                if line in overlap_without_title:
                                    overlap_without_title = overlap_without_title.replace(line, '').strip()
                            candidate_with_overlap = overlap_without_title + '\n' + '\n'.join(lines[current_sub_start:j]) if overlap_without_title else '\n'.join(lines[current_sub_start:j])
                            if len(candidate_with_overlap) <= max_chunk_size:
                                print(f"[INFO] overlap_lines dynamically adjusted to {overlap_lines}")
                                break
                            overlap_lines -= 1
                        # fallback：如果依然过长，则逐行缩减直到满足要求
                        if len(candidate_with_overlap) > max_chunk_size:
                            print(f"[WARNING] fallback triggered at lines {current_sub_start}-{j}")
                            for k in range(j - 1, current_sub_start, -1):
                                overlap_without_title = '\n'.join(tail_overlap.split('\n')[-overlap_lines:])
                                for line in lines[:start]:
                                    if line in overlap_without_title:
                                        overlap_without_title = overlap_without_title.replace(line, '').strip()
                                candidate_with_overlap = overlap_without_title + '\n' + '\n'.join(lines[current_sub_start:k]) if overlap_without_title else '\n'.join(lines[current_sub_start:k])
                                if len(candidate_with_overlap) <= max_chunk_size:
                                    break
                            else:
                                overlap_without_title = '\n'.join(tail_overlap.split('\n')[-overlap_lines:])
                                for line in lines[:start]:
                                    if line in overlap_without_title:
                                        overlap_without_title = overlap_without_title.replace(line, '').strip()
                                candidate_with_overlap = (overlap_without_title + '\n' + '\n'.join(lines[current_sub_start:j]))[:max_chunk_size] if overlap_without_title else '\n'.join(lines[current_sub_start:j])[:max_chunk_size]
                        sub_chunks.append(candidate_with_overlap)
                        print(f"[CHUNK {chunk_count}] sub-chunk length = {len(candidate_with_overlap)}")
                        chunk_count += 1
                        current_sub_start = max(j - overlap_lines, current_sub_start)
                # 添加剩余部分
                overlap_without_title = tail_overlap
                for line in lines[:start]:
                    if line in overlap_without_title:
                        overlap_without_title = overlap_without_title.replace(line, '').strip()
                final_sub_chunk = overlap_without_title + '\n' + '\n'.join(lines[current_sub_start:end]) if overlap_without_title else '\n'.join(lines[current_sub_start:end])
                if final_sub_chunk.strip():
                    sub_chunks.append(final_sub_chunk)
                    print(f"[CHUNK {chunk_count}] final sub-chunk, length = {len(final_sub_chunk)}")
                    chunk_count += 1
                chunks.extend(sub_chunks)

    return chunks

def process_markdown_file(file_path, max_chunk_size=5500, overlap=500):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_text = file.read()
        return split_markdown_into_chunks(markdown_text, max_chunk_size, overlap)
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 未找到。")
        return []
    except Exception as e:
        print(f"错误: 发生了未知错误: {e}")
        return []

def split_markdown_table(file_path, header_lines=5, max_characters=5000):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_table = file.read()
        lines = markdown_table.split('\n')
        header = lines[:header_lines]
        table_data = lines[header_lines:]
        chunks = []
        current_chunk = []
        current_char_count = 0

        for line in table_data:
            line_length = len(line)
            if current_char_count + line_length > max_characters:
                if current_chunk:
                    new_chunk = header + current_chunk
                    chunks.append('\n'.join(new_chunk))
                    current_chunk = []
                    current_char_count = 0

            current_chunk.append(line)
            current_char_count += line_length

        if current_chunk:
            new_chunk = header + current_chunk
            chunks.append('\n'.join(new_chunk))

        return chunks
    except FileNotFoundError:
        print(f"错误：未找到文件 {file_path}。")
        return []
    except Exception as e:
        print(f"发生未知错误：{e}")
        return []

if __name__ == "__main__":
    file_path = '/home/hjb/Health1.1/knowledge_base/test/2015年呼吸内科新增指南及共识大汇总--来源 中华医学会.md'
    chunks = process_markdown_file(file_path)
    # chunks = split_markdown_table(file_path)
    #print(chunks)
    sum = 0
    for i, chunk in enumerate(chunks):
        sum += len(chunk)
        print(f"Chunk {i + 1} (Length: {len(chunk)}):")
        print(chunk)
        print("-" * 50) 
    print(f'sum is :{sum}')